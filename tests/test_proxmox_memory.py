import unittest
from unittest.mock import patch

from app import app


class ProxmoxMemoryTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.requests.get")
    def test_proxmox_memory_endpoint_returns_usage_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "memory": {
                    "used": 2147483648,
                    "total": 4294967296,
                }
            }
        }

        response = self.client.get("/api/proxmox/memory")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["used_gb"], 2.0)
        self.assertEqual(payload["total_gb"], 4.0)
        self.assertEqual(payload["free_gb"], 2.0)
        self.assertEqual(payload["used_percent"], 50.0)

    @patch("app.requests.get")
    def test_proxmox_vms_endpoint_returns_status_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [
                {"vmid": 101, "name": "web-01", "status": "running"},
                {"vmid": 102, "name": "db-01", "status": "stopped"},
            ]
        }

        response = self.client.get("/api/proxmox/vms")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["name"], "web-01")
        self.assertEqual(payload[0]["is_running"], True)
        self.assertEqual(payload[1]["is_running"], False)


if __name__ == "__main__":
    unittest.main()
