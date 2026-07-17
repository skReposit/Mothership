import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenCLAW configuration
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:8000")
POLL_TIMEOUT = 5  # seconds

# Proxmox configuration
PROXMOX_API_URL = os.getenv("PROXMOX_API_URL", "").rstrip("/")
PROXMOX_TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID", "")
PROXMOX_TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET", "")
PROXMOX_NODE = os.getenv("PROXMOX_NODE", "")


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


@app.route("/api/proxmox/memory")
def proxmox_memory():
    """Fetch the current memory usage from the configured Proxmox node."""
    if not all([PROXMOX_API_URL, PROXMOX_TOKEN_ID, PROXMOX_TOKEN_SECRET, PROXMOX_NODE]):
        return jsonify({"error": "Proxmox API configuration is incomplete"}), 400

    headers = {
        "Authorization": f"PVEAPIToken={PROXMOX_TOKEN_ID}={PROXMOX_TOKEN_SECRET}",
    }

    try:
        response = requests.get(
            f"{PROXMOX_API_URL}/api2/json/nodes/{PROXMOX_NODE}/status",
            headers=headers,
            timeout=POLL_TIMEOUT,
        )
        response.raise_for_status()

        payload = response.json().get("data", {})
        memory = payload.get("memory", {}) if isinstance(payload, dict) else {}
        used = int(memory.get("used", 0))
        total = int(memory.get("total", 0))

        if total <= 0:
            return jsonify({"error": "Proxmox memory totals were not returned"}), 502

        used_gb = round(used / (1024 ** 3), 2)
        total_gb = round(total / (1024 ** 3), 2)
        free_gb = round(total_gb - used_gb, 2)
        used_percent = round((used / total) * 100, 2) if total else 0.0

        return jsonify(
            {
                "used_gb": used_gb,
                "total_gb": total_gb,
                "free_gb": free_gb,
                "used_percent": used_percent,
            }
        )

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to the Proxmox API"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to the Proxmox API timed out"}), 504
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc)}), 502
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/api/proxmox/vms")
def proxmox_vms():
    """Fetch the current VM list and runtime state from the configured Proxmox node."""
    if not all([PROXMOX_API_URL, PROXMOX_TOKEN_ID, PROXMOX_TOKEN_SECRET, PROXMOX_NODE]):
        return jsonify({"error": "Proxmox API configuration is incomplete"}), 400

    headers = {
        "Authorization": f"PVEAPIToken={PROXMOX_TOKEN_ID}={PROXMOX_TOKEN_SECRET}",
    }

    try:
        response = requests.get(
            f"{PROXMOX_API_URL}/api2/json/nodes/{PROXMOX_NODE}/qemu",
            headers=headers,
            timeout=POLL_TIMEOUT,
        )
        response.raise_for_status()

        payload = response.json().get("data", [])
        vms = []
        for item in payload if isinstance(payload, list) else []:
            if not isinstance(item, dict):
                continue
            vms.append(
                {
                    "vmid": item.get("vmid"),
                    "name": item.get("name", "Unnamed VM"),
                    "status": item.get("status", "unknown"),
                    "is_running": str(item.get("status", "")).lower() == "running",
                }
            )

        return jsonify(vms)

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to the Proxmox API"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to the Proxmox API timed out"}), 504
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc)}), 502
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
