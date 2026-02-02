from flask import Flask, jsonify
from flask_cors import CORS
from app.database import SessionLocal

app = Flask(__name__)
# Allow all origins for now to prevent blocking, restrict in production if needed
CORS(app, resources={r"/*": {"origins": "*"}})

@app.teardown_appcontext
def shutdown_session(exception=None):
    if SessionLocal:
        SessionLocal.remove()

@app.route("/")
def read_root():
    return jsonify({"message": "Welcome to the Student Progress Tracking API (Flask Version)"})

# Import and Register Blueprints
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.class_routes import class_bp

from app.routes.skill_routes import skill_bp
from app.routes.student_routes import student_bp

from app.routes.analytics_routes import analytics_bp
from app.routes.export_routes import export_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(class_bp)
app.register_blueprint(skill_bp)
app.register_blueprint(student_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(export_bp)