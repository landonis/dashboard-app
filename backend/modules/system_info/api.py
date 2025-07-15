import socket
from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

system_info_bp = Blueprint('system_info', __name__)

@system_info_bp.route('/system-info', methods=['GET'])
@jwt_required()
def get_system_info():
    from backend.user import User  # ← import here to avoid circular import

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    return jsonify({
        "user": user.username if user else "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "hostname": socket.gethostname()
    })
