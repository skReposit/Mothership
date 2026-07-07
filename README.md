# OpenCLAW Web Interface

A lightweight Python web interface for OpenCLAW with a simple textbox for commands and output display.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure OpenCLAW URL
Edit `.env` file and update `OPENCLAW_URL` to match your OpenCLAW instance:
```
OPENCLAW_URL=http://<your-vm-ip>:8000
```

### 3. Run the Application
```bash
python app.py
```

The interface will be available at `http://localhost:5000`

## How It Works

- **Frontend**: Simple HTML/CSS/JavaScript interface with a command input box and output display
- **Backend**: Flask server that:
  - Serves the web interface
  - Receives commands from the frontend via HTTP POST
  - Forwards commands to OpenCLAW HTTP API
  - Returns output to the frontend (poll-based)

## API Endpoint

### POST `/api/command`
**Request:**
```json
{
  "command": "your command here"
}
```

**Response:**
```json
{
  "output": "command output"
}
```

## Important

Make sure your OpenCLAW instance has an HTTP API running on the configured URL. The app expects an `/execute` endpoint that accepts JSON with a `command` field and returns JSON with an `output` field.

If your OpenCLAW API uses a different structure, modify the `/api/command` route in `app.py` accordingly.
