from flask import Blueprint, jsonify, request
from database import get_session
from models import Investigation

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/cases", methods=["GET"])
def get_cases():
    """Retrieve all investigations."""
    try:
        db = get_session()
        cases = db.query(Investigation).order_by(Investigation.id.desc()).all()
        db.close()
        return jsonify([c.to_dict() for c in cases]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/case/<int:case_id>", methods=["DELETE"])
def delete_case(case_id):
    """Delete an investigation by ID."""
    try:
        db = get_session()
        inv = db.query(Investigation).filter_by(id=case_id).first()
        if not inv:
            db.close()
            return jsonify({"error": "Investigation not found"}), 404
        db.delete(inv)
        db.commit()
        db.close()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/report/<int:case_id>", methods=["GET"])
def get_report(case_id):
    """Retrieve a specific investigation."""
    try:
        db = get_session()
        inv = db.query(Investigation).filter_by(id=case_id).first()
        db.close()
        if not inv:
            return jsonify({"error": "Investigation not found"}), 404
        return jsonify(inv.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/investigate", methods=["POST"])
def investigate():
    """Trigger an investigation. For API simplicity, just saves basic info."""
    data = request.json
    if not data or not any([data.get("name"), data.get("username"), data.get("email")]):
        return jsonify({"error": "Please provide name, username, or email"}), 400
    
    # In a full implementation, this would trigger the same pipeline as /search.
    # We will simulate the start of an investigation and return it.
    try:
        db = get_session()
        inv = Investigation(
            subject_name=data.get("name") or data.get("username") or "Unknown",
            username=data.get("username", ""),
            email=data.get("email", ""),
            company=data.get("company", ""),
            status="API Submission",
            analyst="api_user"
        )
        db.add(inv)
        db.commit()
        case_data = inv.to_dict()
        db.close()
        return jsonify({"message": "Investigation started", "case": case_data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
