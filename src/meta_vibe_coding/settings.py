"""Runtime limits shared by the HTTP app and coding-agent wrappers."""

import os
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Limits:
    request_seconds: int = 300
    session_seconds: int = 1800

    def request_budget(self, started_at: float) -> float:
        return max(0, min(self.request_seconds, self.session_seconds - (time.time() - started_at)))


def load_limits() -> Limits:
    values = []
    for name, default in [("MVC_REQUEST_TIMEOUT_SECONDS", 300), ("MVC_SESSION_TIMEOUT_SECONDS", 1800)]:
        try:
            value = int(os.getenv(name, str(default)))
            if value <= 0:
                raise ValueError()
        except ValueError as exc:
            raise ValueError(f"{name} must be a positive integer number of seconds") from exc
        values.append(value)
    if values[1] < values[0]:
        raise ValueError("The session timeout must be at least the request timeout")
    return Limits(*values)
