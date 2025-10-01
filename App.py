# app. py (vulnerable)

from flask import Flask, request, jsonify, current_app
import yaml
import json
import os
import logging


app = Flask(__name__)

# Load configuration from environment and template
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", None)

# Try to read a non-secret template config (if present). Secrets should come from env.
cfg = {}
if os.path.exists("config.template.yaml"):
    with open("config.template.yaml", "r") as f:
        cfg = yaml.safe_load(f) or {}


@app.route("/")
def index():
    return "Lab 4 - vulnerable server"



@app.route("/cause-error")
def cause_error():
    # Raise an exception deliberately (handled and logged)
    try:
        1 / 0
    except Exception as e:
        # Log full exception server-side (not returned to client)
        current_app.logger.exception("Internal error in /cause-error")
        return jsonify({"error": "internal server error"}), 500
    return "won't reach"


@app.route("/admin")
def admin():
    key = request.args.get("key", "")
    # Don't reveal the expected key; only check presence/validity
    if ADMIN_API_KEY is None:
        current_app.logger.warning("ADMIN_API_KEY not set in environment")
        return jsonify({"error": "server not configured"}), 500
    if key != ADMIN_API_KEY:
        return jsonify({"error": "invalid key"}), 401
    # Return limited configuration (no secrets)
    safe_cfg = {k: ("<redacted>" if isinstance(v, dict) else v) for k, v in (cfg.items() if isinstance(cfg, dict) else [])}
    return jsonify({"status": "ok", "cfg": safe_cfg})



@app.route("/deserialize", methods=["POST"])
def deserialize():
    """
    Accept only JSON payloads describing allowed data.
    We intentionally reject binary pickle input.
    Expected content-type: application/json
    Example valid body: {"type": "message", "value": "hello"}
    """
    if not request.is_json:
        return jsonify({"error": "only application/json accepted"}), 415
    payload = request.get_json()
    # Basic validation: allow only simple "message" objects
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid payload"}), 400
    allowed_types = {"message"}
    t = payload.get("type")
    if t not in allowed_types:
       return jsonify({"error": "unsupported type"}), 400
    # Process safe "message" object
    if t == "message":
        value = payload.get("value", "")
        return jsonify({"received_type": "message", "value": str(value)})
    return jsonify({"error": "bad request"}), 400

if __name__ == "__main__":
    # Production-like defaults (do not enable debug)
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)