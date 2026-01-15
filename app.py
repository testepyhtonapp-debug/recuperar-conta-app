from flask import Flask, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import os, random, string, datetime

# ================= APP =================
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 🔥 FORÇAR HTTPS ATRÁS DO RENDER (ESSENCIAL)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ================= CONFIG =================
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ================= EMAIL =================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

# ================= INIT =================
db = SQLAlchemy(app)
mail = Mail(app)
oauth = OAuth(app)

# ================= GOOGLE OAUTH =================
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "email profile"},
)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    reset_code = db.Column(db.String(10))
    reset_expire = db.Column(db.DateTime)

# ================= UTILS =================
def send_email(to, subject, body):
    if not app.config["MAIL_USERNAME"]:
        return
    msg = Message(subject, recipients=[to], body=body)
    mail.send(msg)

def gen_code():
    return "".join(random.choices(string.digits, k=6))

# ================= HOME =================
@app.route("/")
def home():
    return "<h2>Servidor Online ✅</h2><p>Login Google e API ativos.</p>"

# ================= REGISTER =================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter(
        (User.username == data["username"]) | (User.email == data["email"])
    ).first():
        return jsonify(status="error", msg="Conta já existe")

    user = User(
        username=data["username"],
        email=data["email"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(status="ok")

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify(status="error", msg="Dados inválidos")

    return jsonify(status="ok")

# ================= GOOGLE LOGIN =================
@app.route("/login/google")
def login_google():
    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google/callback")
def google_callback():
    token = google.authorize_access_token()
    info = google.get("userinfo").json()

    email = info["email"]
    username = info.get("name", email.split("@")[0])

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=username,
            email=email,
            password="google"
        )
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    return "<h2>Login Google OK ✅</h2><p>Pode voltar para a aplicação.</p>"

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
