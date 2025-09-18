from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Client
from app.utils import admin_required

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/")
@login_required
def index():
    clients = Client.query.order_by(Client.name).all()
    return render_template("clients/list.html", clients=clients)

@clients_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        sector = (request.form.get("sector") or "").strip()
        contact_email = (request.form.get("contact_email") or "").strip()
        if not name:
            flash("Name is required.", "danger")
            return render_template("clients/form.html", client=None)
        c = Client(name=name, sector=sector, contact_email=contact_email)
        db.session.add(c); db.session.commit()
        flash("Client created.", "success")
        return redirect(url_for("clients.index"))
    return render_template("clients/form.html", client=None)

@clients_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    client = Client.query.get_or_404(id)
    if request.method == "POST":
        client.name = (request.form.get("name") or "").strip()
        client.sector = (request.form.get("sector") or "").strip()
        client.contact_email = (request.form.get("contact_email") or "").strip()
        if not client.name:
            flash("Name is required.", "danger")
            return render_template("clients/form.html", client=client)
        db.session.commit()
        flash("Client updated.", "success")
        return redirect(url_for("clients.index"))
    return render_template("clients/form.html", client=client)

@clients_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client); db.session.commit()
    flash("Client deleted.", "warning")
    return redirect(url_for("clients.index"))

