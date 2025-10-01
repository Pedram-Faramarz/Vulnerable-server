# app. py (vulnerable)

from flask import Flask, request, jsonify
import yaml
import pickle
import os

app = Flask(__name__)


# Hardcoded secret key (vulnerable)
ADMIN_API_KEY = "SUPER-SECRET-ADMIN-API-KEY-12345"

# Load configuration file with secrets (vulnerable if committed)

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

@app.route("/")
def index():
    return "Lab 4 - vulnerable server"

# Endpoint that demonstrates interanl error Exposure

@app.route("/cause-error")
def cause_error():
    # raise an exception deliberately (unhandled)
    1 / 0 # ZeroDivisionError -> Flask will return a full stack trace in debug mode or default
    return "won't reach"

# Endpoint that uses the hardcoded secret key
@app.route("/admin")
def admin():
    key = request.args.get("key","")
    if key != ADMIN_API_KEY:
        # return internal message that discloses info
        return jsonify({"error": "Invalid API key", "expected_key": ADMIN_API_KEY}), 401
    return jsonify({"status": "ok", "cfg": cfg})


#unsafe deserialization endpoint
@app.route("/deserialize", methods=["POST"])
def deserialize():
    # Accept raw bytes and unpickle them directly (vulnerable : arbitrary code execution)
    data = request.data
    obj = pickle.loads(data)
    return jsonify({"received" : str(type(obj)), "repr": repr(obj)})

if __name__ == "__main__":
    # Warrning: debug true will show stack traces - intentionaly vulnerable
    app.run(host="0.0.0.0", port=5000, debug=True)