import httpx

DEFAULT_BASE_URL = "http://localhost:8000"

class DevrateAPI:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url

    def check_decision(self, payload: dict) -> dict:
        resp = httpx.post(
            f"{self.base_url}/v1/decision/check",
            json=payload,
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
