#!/usr/bin/env bash
set -euo pipefail

echo "Installing deps..."
pip install -r requirements.txt

echo "Running migrations..."
export FLASK_APP=wsgi:app
flask db upgrade

echo "Seeding admin, user, and demo data (idempotent)..."
python <<'PY'
import os, random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Client, SLA, Incident

app = create_app()
with app.app_context():
    # admin + regular
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_pwd   = os.getenv("ADMIN_PASSWORD", "Admin123!")
    user_email  = os.getenv("USER_EMAIL", "analyst@example.com")
    user_pwd    = os.getenv("USER_PASSWORD", "Analyst123!")

    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(name="Admin", email=admin_email, role="admin",
                     password_hash=generate_password_hash(admin_pwd))
        db.session.add(admin)

    analyst = User.query.filter_by(email=user_email).first()
    if not analyst:
        analyst = User(name="Analyst", email=user_email, role="regular",
                       password_hash=generate_password_hash(user_pwd))
        db.session.add(analyst)
    db.session.commit()

    # ensure 10 clients
    if Client.query.count() < 10:
        sectors = ["Finance","Retail","Public","Manufacturing","Energy"]
        for i in range(1, 11):
            db.session.add(Client(name=f"Client {i}",
                                  sector=random.choice(sectors),
                                  contact_email=f"client{i}@example.com"))
        db.session.commit()

    # ensure 10 SLAs
    if SLA.query.count() < 10:
        tiers = [
            ("Basic",300,1440),("Standard",240,1440),("Standard+",180,720),
            ("Gold",120,480),("Premium",90,360),("Express",60,240),
            ("Platinum",30,120),("Critical",15,60),("Enterprise",45,180),("Bronze",360,2160)
        ]
        for name,resp,reso in tiers:
            db.session.add(SLA(name=name, target_response_mins=resp, target_resolve_mins=reso))
        db.session.commit()

    # ensure 10 incidents
    if Incident.query.count() < 10:
        clients = Client.query.all()
        slas = SLA.query.all()
        creator = analyst or admin
        for i in range(1, 11):
            db.session.add(Incident(
                title=f"Service disruption #{i}",
                description="Seeded incident for demo",
                priority=random.choice(["Low","Medium","High"]),
                status=random.choice(["Open","In-Progress","Resolved","Closed"]),
                client_id=random.choice(clients).id,
                sla_id=random.choice(slas).id,
                created_by=creator.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0,7))
            ))
        db.session.commit()

    print("✅ Seed complete: users, clients(10), slas(10), incidents(10).")
PY

echo "Build script finished."
