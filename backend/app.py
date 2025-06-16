from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from collections import Counter, defaultdict
import os
from scipy.stats import ttest_ind

from util.db import insert_sample, delete_sample, get_con, init_db, get_counts_by_sample, DB_PATH


def create_db():
    """create db if it does not exist on flask start."""
    if not os.path.exists(DB_PATH):
        print("db not found, initing...")
        init_db()
    else:
        print("db found, skipping init")


app = Flask(__name__)
CORS(app)


# run on backend startup
with app.app_context():
    create_db()


@app.route("/")
def index():
    return "API running"


@app.route("/samples", methods=["POST"])
def post_sample():
    try:
        data = request.get_json()
        sample_data = data  # TODO: clean up route and handle
        cell_counts = data.get("cell_counts", {})

        con = get_con()
        insert_sample(con, sample_data, cell_counts)
        con.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        raise e
        return jsonify({"error": str(e)}), 400


@app.route("/samples/<sample_id>", methods=["DELETE"])
def handle_delete_sample(sample_id):
    try:
        con = get_con()
        deleted = delete_sample(con, sample_id)
        con.close()

        if not deleted:
            return jsonify({"error": f"sample {sample_id} not found"}), 404
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


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
    #return jsonify([dict(row) for row in get_counts_by_sample()])
    con = get_con()
    cur = con.cursor()

    cur.execute("""SELECT s.sample_id, s.response, cell_counts.population, cell_counts.count, totals.total_count
                FROM samples s
                JOIN cell_counts ON s.sample_id = cell_counts.sample_id
                JOIN (
                    SELECT sample_id, SUM(count) AS total_count
                    FROM cell_counts
                    GROUP BY sample_id
                ) AS totals ON s.sample_id = totals.sample_id
                WHERE s.sample_type = 'PBMC'""")

    rows = cur.fetchall()

    # format with relative freq
    res = []
    for row in rows:
        sample_id, response, pop, count, total = row
        if total == 0 or response not in ['y', 'n']:
            continue
        rel_freq = (count / total) * 100
        res.append({
            "population": pop,
            "response": response,
            "relative_frequency": rel_freq
        })
    con.close()

    return jsonify(res)


@app.route("/compare-stats", methods=["GET"])
def compare_stats_handle():
    rows = get_counts_by_sample()

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

    return jsonify([res])


@app.route("/filter", methods=["GET"])
def get_filter_summary():
    con = get_con()

    sample_type = request.args.get("sample_type", "PBMC")
    condition = request.args.get("condition", "melanoma")
    treatment = request.args.get("treatment", "tr1")
    time_from_trt_start = request.args.get("time_from_treatment_start", 0)

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

    for samp_id, subj_id, proj, resp, sex in rows:
        sample_ids.append(samp_id)
        projects[proj] += 1
        if resp:
            responses.add((subj_id, resp))
        if sex:
            sexes.add((subj_id, sex))
    
    return jsonify({
        "sample_ids": sample_ids,
        "num_samples_per_project": dict(projects),
        "response_counts": Counter(r for _, r in responses),
        "sex_counts": Counter(s for _, s in sexes)
    })
