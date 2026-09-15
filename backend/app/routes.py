from datetime import datetime

from flask import Blueprint, Response, jsonify, request

from app import db
from app.models import Contact, ContactEmail, Sequence, SequenceEvent
from app.tracking import TRACKING_PIXEL_PNG
from config import Config

api_bp = Blueprint("api", __name__)


@api_bp.get("/api/sequences")
def list_sequences():
    sequences = Sequence.query.order_by(Sequence.created_at.desc()).all()

    result = []
    for seq in sequences:
        opened_count = sum(1 for e in seq.events if e.opened_at is not None)
        result.append(
            {
                "id": seq.id,
                "contact_name": seq.contact.name,
                "subject": seq.subject,
                "status": seq.status,
                "current_step": seq.current_step,
                "sent_count": len(seq.events),
                "opened_count": opened_count,
                "last_sent_at": (
                    seq.last_sent_at.isoformat() if seq.last_sent_at else None
                ),
            }
        )

    return jsonify({"sequences": result, "tracking_enabled": Config.tracking_enabled()})


@api_bp.post("/api/contacts")
def create_contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    subject = (data.get("subject") or "").strip()
    first_body = (data.get("first_body") or "").strip()
    followup1_body = (data.get("followup1_body") or "").strip() or None
    followup2_body = (data.get("followup2_body") or "").strip() or None

    emails_raw = data.get("emails")
    if isinstance(emails_raw, str):
        emails = [e.strip() for e in emails_raw.split(",") if e.strip()]
    elif isinstance(emails_raw, list):
        emails = [str(e).strip() for e in emails_raw if str(e).strip()]
    else:
        emails = []

    missing = [
        field
        for field, value in [
            ("name", name),
            ("emails", emails),
            ("subject", subject),
            ("first_body", first_body),
        ]
        if not value
    ]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    contact = Contact(name=name)
    contact.emails = [ContactEmail(email=e) for e in emails]

    sequence = Sequence(
        contact=contact,
        subject=subject,
        first_body=first_body,
        followup1_body=followup1_body,
        followup2_body=followup2_body,
        status=Sequence.STATUS_PENDING,
        current_step=0,
    )

    db.session.add(contact)
    db.session.add(sequence)
    db.session.commit()

    # Sending happens asynchronously via the background worker (app/worker.py),
    # so this request returns immediately once the sequence is recorded.

    return jsonify({"id": sequence.id, "contact_id": contact.id}), 201


@api_bp.get("/track/<tracking_id>.png")
def track_open(tracking_id):
    event = SequenceEvent.query.filter_by(tracking_id=tracking_id).first()
    if event is not None and event.opened_at is None:
        event.opened_at = datetime.utcnow()
        db.session.commit()

    # Always return a valid pixel, even for an unrecognized tracking_id -
    # never error back to the recipient's mail client.
    return Response(TRACKING_PIXEL_PNG, mimetype="image/png")
