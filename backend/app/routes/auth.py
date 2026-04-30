from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app.extensions import db, bcrypt
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


# ── Register ────────────────────────────────────────────
@auth_bp.post("/register")
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(email=email, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# ── Login ───────────────────────────────────────────────
@auth_bp.post("/login")
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": str(user.id),
            "email": user.email
        }
    }), 200


# ── Me (Protected) ──────────────────────────────────────
@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": str(user.id),
        "email": user.email
    })


# ── Logout (stateless for now) ──────────────────────────
@auth_bp.post("/logout")
def logout():
    # JWT is stateless — frontend deletes token
    return jsonify({"message": "Logged out"}), 200
