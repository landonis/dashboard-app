@@ .. @@
 import socket
 from datetime import datetime
 from flask import Blueprint, jsonify
 from flask_jwt_extended import jwt_required, get_jwt_identity
-from app import User
 import logging

 logger = logging.getLogger(__name__)

+# Import User model - handle different import paths
+try:
+    from backend.app import User
+except ImportError:
+    try:
+        from app import User
+    except ImportError:
+        # Fallback for when running from different contexts
+        import sys
+        import os
+        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
+        from app import User
+
 # Create blueprint
 system_info_bp = Blueprint('system_info', __name__)