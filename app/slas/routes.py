from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import SLA
from app.utils import admin_required

slas_bp = Blueprint("slas", __name__)

@slas_bp.route("/")
@login_required
def index():
    slas = SLA.query.order_by(SLA.name).all()
    return render_template("slas/list.html", slas=slas)

@slas_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        try:
            resp = int(request.form.get("target_response_mins") or 0)
            reso = int(request.form.get("target_resolve_mins") or 0)
        except ValueError:
            resp = reso = 0
        if not name or not resp or not reso:
            flash("Name, response and resolve minutes are required.", "danger")
            return render_template("slas/form.html", sla=None)
        s = SLA(name=name, target_response_mins=resp, target_resolve_mins=reso)
        db.session.add(s); db.session.commit()
        flash("SLA created.", "success")
        return redirect(url_for("slas.index"))
    return render_template("slas/form.html", sla=None)

@slas_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    sla = SLA.query.get_or_404(id)
    if request.method == "POST":
        sla.name = (request.form.get("name") or "").strip()
        try:
            sla.target_response_mins = int(request.form.get("target_response_mins") or 0)
            sla.target_resolve_mins = int(request.form.get("target_resolve_mins") or 0)
        except ValueError:
            flash("Response/Resolve minutes must be integers.", "danger")
            return render_template("slas/form.html", sla=sla)
        if not sla.name or sla.target_response_mins <= 0 or sla.target_resolve_mins <= 0:
            flash("All fields are required.", "danger")
            return render_template("slas/form.html", sla=sla)
        db.session.commit()
        flash("SLA updated.", "success")
        return redirect(url_for("slas.index"))
    return render_template("slas/form.html", sla=sla)

@slas_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    sla = SLA.query.get_or_404(id)
    db.session.delete(sla); db.session.commit()
    flash("SLA deleted.", "warning")
    return redirect(url_for("slas.index"))
