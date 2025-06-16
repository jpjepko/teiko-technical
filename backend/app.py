from flask import Flask, request, jsonify
from flask_cors import CORS

from util.db import *


app = Flask(__name__)
CORS(app)


# run on backend startup
with app.app_context():
    create_db()


@app.route("/")
def index():
    return "API running"


@app.route("/samples", methods=["POST"])
def handle_post_sample():
    try:
        data = request.get_json()
        sample_data = data
        cell_counts = data.get("cell_counts", {})

        insert_sample(sample_data, cell_counts)
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/samples/<sample_id>", methods=["DELETE"])
def handle_delete_sample(sample_id):
    try:
        deleted = delete_sample(sample_id)

        if not deleted:
            return jsonify({"error": f"sample {sample_id} not found"}), 404
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/samples", methods=["GET"])
def handle_samples():
    return jsonify(get_samples())


@app.route("/summary", methods=["GET"])
def handle_summary():
    return jsonify(get_summary_list())


@app.route("/compare", methods=["GET"])
def handle_compare():
    return jsonify(get_freqs_by_response("PBMC"))


@app.route("/compare-significance", methods=["GET"])
def handle_compare_significance():
    return jsonify(get_significance("PBMC", "tr1", "melanoma"))


@app.route("/filter", methods=["GET"])
def handle_filter():
    sample_type = request.args.get("sample_type", "PBMC")
    condition = request.args.get("condition", "melanoma")
    treatment = request.args.get("treatment", "tr1")
    time_from_trt_start = request.args.get("time_from_treatment_start", 0)

    return jsonify(get_filter_summary(sample_type, condition, treatment, time_from_trt_start))
