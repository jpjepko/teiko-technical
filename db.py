import sqlite3
import pandas as pd


CSV_FILE = "cell-count.csv"
DB_FILE = "cell-count.db"
SCHEMA_FILE = "schema.sql"


def main():
    try:
        with open(DB_FILE, "r") as f:
            pass
    except FileNotFoundError:
        init_db()


def init_db():
    """Init db from schema and populate with csv data."""
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    with open(SCHEMA_FILE) as fp:
        cur.executescript(fp.read())

    df = pd.read_csv(CSV_FILE)

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


def insert_sample(con, sample_data: dict, cell_counts: dict):
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


def remove_sample(con, sample_id: str):
    cur = con.cursor()

    # fetch subject_id
    cur.execute("SELECT subject_id FROM samples WHERE sample_id = ?", (sample_id, ))
    row = cur.fetchone()
    if not row:
        print(f"sample {sample_id} not found.")
        return
    subject_id = row[0]

    cur.execute("DELETE FROM cell_counts WHERE sample_id = ?", (sample_id, ))
    cur.execute("DELETE FROM samples WHERE sample_id = ?", (sample_id, ))

    # delete subject if no samples remain
    cur.execute("SELECT 1 FROM samples WHERE subject_id = ?", (subject_id, ))
    if cur.fetchone() is None:
        cur.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id, ))

    con.commit()


if __name__ == "__main__":
    main()
