from flask import Flask, redirect, url_for
from config import Config
from extensions import db, mail
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.dashboard import dashboard_bp
from routes.chatbot import chatbot_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(chatbot_bp)

# Create all DB tables on startup (works with gunicorn too)
with app.app_context():
    db.create_all()

# Home route (entry point)
@app.route("/")
def home():
    return redirect(url_for("auth.login"))

# Run App (local development only)
if __name__ == "__main__":
    app.run(debug=True)