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


if __name__ == "__main__":
    unittest.main()
