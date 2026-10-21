import json
import logging


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(json.loads(record.getMessage()))


def test_access_log_records_client_ip_and_user_agent(client):
    capture = _Capture()
    access_log = logging.getLogger("access")
    access_log.addHandler(capture)
    try:
        client.get("/missing", headers={"User-Agent": "zgrab/0.x"},
                   environ_base={"REMOTE_ADDR": "203.0.113.7"})
    finally:
        access_log.removeHandler(capture)

    line = capture.lines[-1]
    assert line["type"] == "access"
    assert line["status"] == 404
    assert line["ip"] == "203.0.113.7"
    assert line["user_agent"] == "zgrab/0.x"
