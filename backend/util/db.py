import sqlite3
import pandas as pd
import os
from scipy.stats import ttest_ind
from collections import Counter, defaultdict

PATH = "data/cell-count.csv"
DB_PATH = "db/database.db"
SCHEMA_PATH = "db/schema.sql"


def create_db():
    """create db if it does not exist on flask start."""
    print("CREATE")
    if not os.path.exists(DB_PATH):
        print("db not found, initing...")
        _init_db()
    else:
        print("db found, skipping init")


def _init_db():
    """Init db from schema and populate with csv data."""
    print("INIT")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    with open(SCHEMA_PATH) as fp:
        cur.executescript(fp.read())

    df = pd.read_csv(PATH)

    # fill in subjects
    uniq_subjs = df[["subject", "project", "condition", "age", "sex"]].drop_duplicates(subset="subject")
    subj_tuples = [tuple(row[1:]) for row in uniq_subjs.itertuples()]   # drop pandas series id from tuple
    cur.executemany("INSERT INTO subjects VALUES(?, ?, ?, ?, ?)", subj_tuples)
    con.commit()

    # fill in samples
    uniq_samps = df[["sample", "subject", "treatment", "response", "sample_type", "time_from_treatment_start"]].drop_duplicates(subset="sample")
    samp_tuples = [tuple(row[1:]) for row in uniq_samps.itertuples()]   # drop pandas series id from tuple
    cur.executemany("INSERT INTO samples VALUES(?, ?, ?, ?, ?, ?)", samp_tuples)
    con.commit()

    # fill in cell_counts
    for _, row in df.iterrows():
        sample_id = row["sample"]
        pop_cols = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
        data = [(row["sample"], pop, row[pop]) for pop in pop_cols]
        cur.executemany("""
                        INSERT INTO cell_counts (sample_id, population, count)
                        VALUES (?, ?, ?)""", data)
    con.commit()
    con.close()


def _get_con():
    """return con object that returns dicts from db (not tuples). Must be closed after use."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def get_samples():
    con = _get_con()
    cur = con.execute("SELECT * FROM samples")
    samples = [dict(row) for row in cur.fetchall()]
    con.close()
    return samples


def get_summary_list():
    samples = get_samples()
    con = _get_con()
    cur = con.cursor()
    summary_list = []

    for sample in samples:
        sample_id = sample["sample_id"]
        cur.execute("SELECT * FROM cell_counts WHERE sample_id = ?", (sample_id, ))
        pops = [dict(row) for row in cur.fetchall()]
        total_count = sum([pop["count"] for pop in pops])

        for pop in pops:
            summary_list.append({
                "sample_id": pop["sample_id"],
                "total_count": total_count,
                "population": pop["population"],
                "count": pop["count"],
                "relative_frequency": 100.0 * pop["count"] / total_count
            })

    con.close()
    return summary_list


def get_freqs_by_response(sample_type):
    """return list of relative freqs, grouped by cell pop and response."""
    con = _get_con()
    cur = con.execute("""SELECT
                          samples.sample_id,
                          samples.response,
                          cell_counts.population,
                          cell_counts.count,
                          totals.total_count
                      FROM samples
                      JOIN cell_counts ON samples.sample_id = cell_counts.sample_id
                      JOIN (
                          SELECT sample_id, SUM(count) AS total_count
                          FROM cell_counts
                          GROUP BY sample_id
                      ) AS totals ON samples.sample_id = totals.sample_id
                      WHERE samples.sample_type = ?""", (sample_type, ))

    rows = cur.fetchall()
    con.close()

    # format with relative freq
    res = []
    for row in rows:
        sample_id, response, pop, count, total = row
        if total == 0 or response not in ['y', 'n']:
            continue
        rel_freq = (count / total) * 100.0
        res.append({
            "population": pop,
            "response": response,
            "relative_frequency": rel_freq
        })
    
    return res


def get_significance(sample_type, treatment, condition):
    """run t-test on filtered pops, grouped by response."""
    con = _get_con()
    cur = con.execute("""SELECT
                          samples.sample_id,
                          samples.response,
                          cell_counts.population,
                          cell_counts.count
                      FROM samples
                      JOIN subjects ON samples.subject_id = subjects.subject_id
                      JOIN cell_counts ON samples.sample_id = cell_counts.sample_id
                      WHERE
                          samples.sample_type = ?
                          AND samples.treatment = ?
                          AND subjects.condition = ?
                          AND samples.response IN ('y', 'n')""",
                      (sample_type, treatment, condition))

    rows = cur.fetchall()
    con.close()

    # organize by sample
    samples = defaultdict(lambda: {
        "response": None,
        "populations": defaultdict(int)
    })

    for sample_id, response, pop, count in rows:
        samples[sample_id]["response"] = response
        samples[sample_id]["populations"][pop] += count

    # relative freq dataset
    pop_groups = defaultdict(lambda: {"y": [], "n": []})
    for sample_id, data in samples.items():
        total = sum(data["populations"].values())
        if total == 0:
            continue
        for pop, count in data["populations"].items():
            freq = (count / total) * 100
            pop_groups[pop][data["response"]].append(freq)

    # t-tests
    res = []
    for pop, groups in pop_groups.items():
        y_vals = groups["y"]
        n_vals = groups["n"]
        if len(y_vals) < 2 or len(n_vals) < 2:
            pval = None # insufficient data
        else:
            _, pval = ttest_ind(y_vals, n_vals, equal_var=False)
        res.append({
            "population": pop,
            "p_value": round(pval, 4) if pval is not None else None,
            "significant": bool(pval is not None and pval < 0.05)
        })
    
    return res


def get_filter_summary(sample_type, condition, treatment, time_from_trt_start):
    """apply filter and return counts of samples and subjects."""
    con = _get_con()
    cur = con.execute("""SELECT
                          samples.sample_id,
                          samples.subject_id,
                          subjects.project,
                          samples.response,
                          subjects.sex
                      FROM samples
                      JOIN subjects ON samples.subject_id = subjects.subject_id
                      WHERE
                          samples.sample_type = ?
                          AND samples.time_from_treatment_start = ?
                          AND samples.treatment = ?
                          AND subjects.condition = ?""",
                      (sample_type, time_from_trt_start, treatment, condition))
    rows = cur.fetchall()
    con.close()

    sample_ids = []
    projects = Counter()
    responses = set()   # use set to count subjects, not samples
    sexes = set()
    
    for sample_id, subject_id, project, response, sex in rows:
        sample_ids.append(sample_id)
        projects[project] += 1

        if response:
            responses.add((subject_id, response))
        if sex:
            responses.add((subject_id, sex))
    
    # TODO: debug non-default inputs (ttt=7)

    return {
        "sample_ids": sample_ids,
        "num_samples_per_project": dict(projects),
        "response_counts": Counter(r for _, r in responses),
        "sex_counts": Counter(s for _, s in sexes)
    }


def insert_sample(sample_data: dict, cell_counts: dict = {}):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # check if subject exists
    cur.execute("SELECT 1 FROM subjects WHERE subject_id = ?", (sample_data["subject_id"], ))
    if cur.fetchone() is None:
        # insert new subject
        cur.execute("""
                    INSERT INTO subjects (subject_id, project, condition, age, sex)
                    VALUES (?, ?, ?, ?, ?)""",
                    (sample_data["subject_id"], sample_data["project"], sample_data["condition"],
                     sample_data["age"], sample_data["sex"]))
    con.commit()

    # insert sample
    cur.execute("""
                INSERT INTO samples (sample_id, subject_id, treatment, response, sample_type, time_from_treatment_start)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (sample_data["sample_id"], sample_data["subject_id"], sample_data["treatment"],
                 sample_data["response"], sample_data["sample_type"], sample_data["time_from_treatment_start"]))

    # insert cell_counts
    for pop, count in cell_counts.items():
        cur.execute("""
                    INSERT INTO cell_counts (sample_id, population, count)
                    VALUES (?, ?, ?)""", (sample_data["sample_id"], pop, count))
    con.commit()
    con.close()


def delete_sample(sample_id: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # fetch subject_id
    cur.execute("SELECT subject_id FROM samples WHERE sample_id = ?", (sample_id, ))
    row = cur.fetchone()
    if not row:
        print(f"sample {sample_id} not found.")
        return False
    subject_id = row[0]

    cur.execute("DELETE FROM cell_counts WHERE sample_id = ?", (sample_id, ))
    cur.execute("DELETE FROM samples WHERE sample_id = ?", (sample_id, ))

    # delete subject if no samples remain
    cur.execute("SELECT 1 FROM samples WHERE subject_id = ?", (subject_id, ))
    if cur.fetchone() is None:
        cur.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id, ))

    con.commit()
    con.close()
    return True
