from app.services.auth import needs_reauth, should_trigger_persona
from app.services.batch import BatchSplitter
from app.services.client import BrainClient


class FakeResponse:
    def __init__(self, status_code: int, headers: dict | None = None):
        self.status_code = status_code
        self.headers = headers or {}


def test_persona_fallback_is_detected():
    response = FakeResponse(401, {"WWW-Authenticate": "persona"})
    assert should_trigger_persona(response) is True
    assert needs_reauth(response) is True


def test_client_parses_recordset_payload():
    payload = {"schema": ["pnl", "sharpe"], "records": [[1.2, 1.5], [0.8, 1.1]]}
    client = BrainClient()
    assert client.parse_recordset(payload) == payload


def test_batch_splitter_keeps_like_configurations_together():
    items = [
        {"region": "USA", "delay": 1, "language": "en", "instrumentType": "equity"},
        {"region": "USA", "delay": 1, "language": "en", "instrumentType": "equity"},
        {"region": "EUR", "delay": 1, "language": "en", "instrumentType": "equity"},
    ]
    batches = BatchSplitter(max_batch_size=2).split_by_settings(items)
    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert batches[1][0]["region"] == "EUR"
