import sqlite3
import pandas as pd


CSV_FILE = "cell-count.csv"
DB_FILE = "cell-count.db"
SCHEMA_FILE = "schema.sql"


def main():
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

if __name__ == "__main__":
    main()
