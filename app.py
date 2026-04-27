"""
QuickFood — Application principale
Architecture Blueprint propre, corrigée et optimisée.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from extensions import db, login_manager, migrate, socketio


# ─────────────────────────────────────────────
# 🔥 SEED ADMIN (DOIT ÊTRE EN HAUT)
# ─────────────────────────────────────────────
def _seed_admin():
    from models.user import User
    from werkzeug.security import generate_password_hash
    from datetime import datetime

    if not User.query.filter_by(email="admin@quickfood.sn").first():
        admin = User(
            name="Admin",
            email="admin@quickfood.sn",
            password=generate_password_hash(
                os.environ.get("ADMIN_PASSWORD", "admin123")
            ),
            role="admin",
            is_admin=True,
            created_at=datetime.utcnow(),
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Compte admin créé : admin@quickfood.sn")


# ─────────────────────────────────────────────
# 🚀 CREATE APP
# ─────────────────────────────────────────────
def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ─────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    # ── User loader ─────────────────────────────
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Blueprints ──────────────────────────────
    from routes.main    import main_bp
    from routes.auth    import auth_bp
    from routes.cart    import cart_bp
    from routes.client  import client_bp
    from routes.partner import partner_bp
    from routes.admin   import admin_bp
    from routes.api     import api_bp
    from routes.payment import payment_bp
    from routes.support import support_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(partner_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(support_bp)

    # ── Sockets ────────────────────────────────
    import sockets  # noqa: F401

    # ── Sécurité ────────────────────────────────
    from utils.security import apply_security_headers, generate_csrf_token

    @app.after_request
    def add_security_headers(response):
        return apply_security_headers(response)

    # ── Context global ──────────────────────────
    from services.cart_service import CartService
    from flask import session

    @app.context_processor
    def inject_globals():
        return {
            "cart_count": CartService.count(session),
            "csrf_token": generate_csrf_token,
        }

    # ── Template filter ─────────────────────────
    @app.template_filter("format_number")
    def format_number(value):
        try:
            return "{:,.0f}".format(float(value)).replace(",", " ")
        except (ValueError, TypeError):
            return value

    # ── DB INIT ────────────────────────────────
    with app.app_context():
        instance_dir = os.path.join(os.path.dirname(__file__), "instance")
        os.makedirs(instance_dir, exist_ok=True)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        from models.support import SupportTicket  # noqa
        from models.virement import Virement     # noqa

        db.create_all()
        _seed_admin()

    # ── Service Worker ─────────────────────────
    @app.route("/sw.js")
    def service_worker():
        from flask import send_from_directory
        return send_from_directory(
            app.static_folder,
            "sw.js",
            mimetype="application/javascript"
        )

    return app


# ─────────────────────────────────────────────
# 🌍 IMPORTANT POUR GUNICORN / DIGITALOCEAN
# ─────────────────────────────────────────────
app = create_app()


# ─────────────────────────────────────────────
# 🧪 LANCEMENT LOCAL
# ─────────────────────────────────────────────
if __name__ == "__main__":
    socketio.run(app, debug=True)