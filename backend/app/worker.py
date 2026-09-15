"""Background worker: on a recurring interval, sends the first message for
pending sequences and evaluates replies/follow-ups for active ones.

Scaffold only for now - the scheduling loop and global throttle primitives
(rolling 24h cap, randomized inter-send delay) are wired up here since they
don't depend on Graph, but the actual send / reply-check logic is a TODO
that lands once app/graph_client.py is implemented in a follow-up commit.
"""

import random
import threading
from datetime import datetime, timedelta

from app import db
from app.models import SendLog
from config import Config


def can_send_now() -> bool:
    """Rolling 24h send cap (MAX_EMAILS_PER_DAY), enforced globally across
    all contacts and sequence steps."""
    cutoff = datetime.utcnow() - timedelta(days=1)
    sent_last_24h = SendLog.query.filter(SendLog.sent_at >= cutoff).count()
    return sent_last_24h < Config.MAX_EMAILS_PER_DAY


def record_send() -> None:
    db.session.add(SendLog())
    db.session.commit()


def throttle_delay_seconds() -> int:
    """Randomized delay to enforce between every individual outbound send."""
    return random.randint(Config.MIN_DELAY_SECONDS, Config.MAX_DELAY_SECONDS)


def run_cycle(app) -> None:
    """One pass over all sequences.

    TODO (follow-up commit):
      - pending sequences -> send first message (respecting can_send_now() +
        throttle_delay_seconds() between each send)
      - active sequences -> check Inbox for a reply from any of the
        contact's emails since last_sent_at; if found, mark `replied` and
        stop; otherwise, if FOLLOWUP_1_DAYS/FOLLOWUP_2_DAYS have elapsed,
        send the next configured follow-up (or skip straight to
        `completed` if that follow-up's body is blank)
    """
    with app.app_context():
        pass


class Worker:
    """Runs run_cycle() on a background thread every
    Config.WORKER_INTERVAL_SECONDS, independent of the frontend/API."""

    def __init__(self, app):
        self.app = app
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            run_cycle(self.app)
            self._stop_event.wait(Config.WORKER_INTERVAL_SECONDS)
