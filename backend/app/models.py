import uuid
from datetime import datetime

from app import db


def _new_tracking_id() -> str:
    return uuid.uuid4().hex


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    emails = db.relationship(
        "ContactEmail", backref="contact", cascade="all, delete-orphan"
    )
    sequences = db.relationship(
        "Sequence", backref="contact", cascade="all, delete-orphan"
    )


class ContactEmail(db.Model):
    __tablename__ = "contact_emails"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)
    email = db.Column(db.String(255), nullable=False)


class Sequence(db.Model):
    __tablename__ = "sequences"

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_REPLIED = "replied"
    STATUS_COMPLETED = "completed"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    first_body = db.Column(db.Text, nullable=False)
    followup1_body = db.Column(db.Text, nullable=True)
    followup2_body = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    current_step = db.Column(db.Integer, nullable=False, default=0)
    last_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship(
        "SequenceEvent", backref="sequence", cascade="all, delete-orphan"
    )


class SequenceEvent(db.Model):
    """One row per actual send (first message or a follow-up)."""

    __tablename__ = "sequence_events"

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey("sequences.id"), nullable=False)
    step = db.Column(db.Integer, nullable=False)
    to_email = db.Column(db.String(255), nullable=False)
    tracking_id = db.Column(
        db.String(64), unique=True, nullable=False, default=_new_tracking_id
    )
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened_at = db.Column(db.DateTime, nullable=True)


class SendLog(db.Model):
    """One row per outbound send, system-wide. Used only to enforce the
    rolling 24h send cap and the global inter-send delay - not tied to a
    specific contact or sequence."""

    __tablename__ = "send_log"

    id = db.Column(db.Integer, primary_key=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
