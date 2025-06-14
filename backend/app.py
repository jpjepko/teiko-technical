from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from collections import Counter


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


#@app.route("/compare", methods=["GET"])


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

