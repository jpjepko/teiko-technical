from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from collections import Counter, defaultdict

from scipy.stats import ttest_ind


app = Flask(__name__)
CORS(app)
DB_PATH = "db/cell-count.db"


def get_con():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


@app.route("/")
def index():
    return "API running"


@app.route("/samples", methods=["GET"])
def list_samples():
    con = get_con()

    cur = con.execute("SELECT * FROM samples")
    samples = [dict(row) for row in cur.fetchall()]
    con.close()
    return jsonify(samples)


@app.route("/summary", methods=["GET"])
def summary():
    con = get_con()
    cur = con.execute("SELECT * FROM samples")
    samples = [dict(row) for row in cur.fetchall()]
    summary_list = []

    for sample in samples:
        sample_id = sample["sample_id"]
        cur = con.execute("SELECT * FROM cell_counts WHERE sample_id = ?", (sample_id, ))
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
    return jsonify(summary_list)


@app.route("/compare", methods=["GET"])
def compare_handle():
    con = get_con()
    cur = con.cursor()
    cur.execute("""
                SELECT
                    samples.sample_id,
                    samples.response,
                    cell_counts.population,
                    cell_counts.count
                FROM samples
                JOIN subjects ON samples.subject_id = subjects.subject_id
                JOIN cell_counts ON samples.sample_id = cell_counts.sample_id
                WHERE
                    samples.sample_type = 'PBMC'
                    AND samples.treatment = 'tr1'
                    AND subjects.condition = 'melanoma'
                    AND samples.response IN ('y', 'n')""")
    return jsonify([dict(row) for row in cur.fetchall()])


@app.route("/compare-stats", methods=["GET"])
def compare_stats_handle():
    # TODO: copied from /compare, move into function to avoid duplication
    con = get_con()
    cur = con.cursor()
    cur.execute("""
                SELECT
                    samples.sample_id,
                    samples.response,
                    cell_counts.population,
                    cell_counts.count
                FROM samples
                JOIN subjects ON samples.subject_id = subjects.subject_id
                JOIN cell_counts ON samples.sample_id = cell_counts.sample_id
                WHERE
                    samples.sample_type = 'PBMC'
                    AND samples.treatment = 'tr1'
                    AND subjects.condition = 'melanoma'
                    AND samples.response IN ('y', 'n')""")
    
    rows = cur.fetchall()

    # organize by sample
    samples = defaultdict(lambda: {
        "response": None,
        "populations": defaultdict(int)
    })

    for samp_id, resp, pop, count in rows:
        samples[samp_id]["response"] = resp
        samples[samp_id]["populations"][pop] += count

    # relative freq dataset
    pop_groups = defaultdict(lambda: {"y": [], "n": []})
    for samp_id, data in samples.items():
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

    print(res)
    return jsonify([res])


@app.route("/filter", methods=["GET"])
def get_filter_summary():
    con = get_con()

    cur = con.execute("""
                      SELECT
                          samples.sample_id,
                          samples.subject_id,
                          subjects.project,
                          samples.response,
                          subjects.sex
                      FROM samples
                      JOIN subjects ON samples.subject_id = subjects.subject_id
                      WHERE
                          samples.sample_type = 'PBMC'
                          AND samples.time_from_treatment_start = 0
                          AND samples.treatment = 'tr1'
                          AND subjects.condition = 'melanoma'""")
    rows = cur.fetchall()
    
    samp_ids = []
    projs = Counter()
    resps = set()   # use set to count subjects, not samples
    sexes = set()

    for samp_id, subj_id, proj, resp, sex in rows:
        samp_ids.append(samp_id)
        projs[proj] += 1
        if resp:
            resps.add((subj_id, resp))
        if sex:
            sexes.add((subj_id, sex))
    
    return jsonify({
        "sample_ids": samp_ids,
        "num_samples_per_project": dict(projs),
        "response_counts": Counter(r for _, r in resps),
        "sex_counts": Counter(s for _, s in sexes)
    })
