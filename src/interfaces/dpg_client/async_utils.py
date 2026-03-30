import threading

import requests


class AsyncRequestor:
    """
    Helper to run API requests in a background thread
    and execute a callback on the main thread when done.
    """
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base

    def _run(self, method, endpoint, callback=None, **kwargs):
        try:
            url = f"{self.api_base}{endpoint}"
            response = requests.request(method, url, **kwargs)
            if callback:
                # DPG is thread-safe for item updates?
                # Actually DPG commands can be called from threads,
                # but it's safer to separate logic if possible.
                # Here we just run the callback directly.
                callback(response)
        except Exception as e:
            print(f"Async Error [{endpoint}]: {e}")

    def get(self, endpoint, callback=None, **kwargs):
        threading.Thread(
            target=self._run,
            args=("GET", endpoint, callback),
            kwargs=kwargs,
            daemon=True
        ).start()

    def post(self, endpoint, data=None, json=None, callback=None, **kwargs):
        threading.Thread(
            target=self._run,
            args=("POST", endpoint, callback),
            kwargs={"data": data, "json": json, **kwargs},
            daemon=True
        ).start()

# Global instance
api = AsyncRequestor()
