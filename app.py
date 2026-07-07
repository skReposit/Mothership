import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenCLAW configuration
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:8000")
POLL_TIMEOUT = 5  # seconds


@app.route("/")
def index():
    """Serve the web interface"""
    return render_template("index.html")


@app.route("/api/command", methods=["POST"])
def execute_command():
    """Execute a command on OpenCLAW and return the output"""
    data = request.json
    command = data.get("command", "").strip()

    if not command:
        return jsonify({"error": "Command cannot be empty"}), 400

    try:
        # Send command to OpenCLAW HTTP API
        # Adjust the endpoint based on your OpenCLAW API structure
        response = requests.post(
            f"{OPENCLAW_URL}/execute",
            json={"command": command},
            timeout=POLL_TIMEOUT,
        )

        if response.status_code == 200:
            output = response.json().get("output", "No output")
            return jsonify({"output": output})
        else:
            return jsonify({"error": f"OpenCLAW error: {response.text}"}), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to OpenCLAW instance"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to OpenCLAW timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
