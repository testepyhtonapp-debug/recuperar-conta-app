from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
import os, random, string, datetime

app = Flask(__name__)

# ================= CONFIG =================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "super-secret-key"

# EMAIL
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

# GOOGLE
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

db = SQLAlchemy(app)
mail = Mail(app)
oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "openid email profile"}
)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    google_id = db.Column(db.String(200))
    photo = db.Column(db.String(300))
    reset_code = db.Column(db.String(10))
    reset_expire = db.Column(db.DateTime)

# ================= UTILS =================
def send_email(to, subject, body):
    msg = Message(subject, recipients=[to], body=body)
    mail.send(msg)

def gen_code():
    return "".join(random.choices(string.digits, k=6))

# ================= AUTH =================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter(
        (User.username == data["username"]) | (User.email == data["email"])
    ).first():
        return jsonify(status="error", msg="Conta já existe")

    u = User(
        username=data["username"],
        email=data["email"],
        password=data["password"]
    )
    db.session.add(u)
    db.session.commit()
    return jsonify(status="ok")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    u = User.query.filter_by(
        username=data["username"],
        password=data["password"]
    ).first()

    if not u:
        return jsonify(status="error", msg="Dados inválidos")
    return jsonify(status="ok")

# ================= GOOGLE =================
@app.route("/login/google")
def login_google():
    return google.authorize_redirect(GOOGLE_REDIRECT_URI)

@app.route("/login/google/callback")
def google_callback():
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()

    user = User.query.filter_by(email=user_info["email"]).first()

    if not user:
        user = User(
            username=user_info["email"].split("@")[0],
            email=user_info["email"],
            google_id=user_info["id"],
            photo=user_info.get("picture")
        )
        db.session.add(user)
        db.session.commit()

    return "Login Google efetuado com sucesso. Pode fechar esta janela."

# ================= RECOVER USERNAME =================
@app.route("/recover-username", methods=["POST"])
def recover_username():
    email = request.json["email"]
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error")

    send_email(
        email,
        "Recuperar Utilizador",
        f"O teu nome de utilizador é: {user.username}"
    )
    return jsonify(status="ok")

# ================= RECOVER PASSWORD =================
@app.route("/recover-password", methods=["POST"])
def recover_password():
    email = request.json["email"]
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error")

    code = gen_code()
    user.reset_code = code
    user.reset_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    db.session.commit()

    send_email(
        email,
        "Código de recuperação",
        f"O teu código é: {code}"
    )
    return jsonify(status="ok")

@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or user.reset_code != data["code"]:
        return jsonify(status="error", msg="Código inválido")

    if datetime.datetime.utcnow() > user.reset_expire:
        return jsonify(status="error", msg="Código expirado")

    user.password = data["new_password"]
    user.reset_code = None
    user.reset_expire = None
    db.session.commit()

    return jsonify(status="ok")

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
