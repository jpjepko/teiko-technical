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


if __name__ == "__main__":
    main()
