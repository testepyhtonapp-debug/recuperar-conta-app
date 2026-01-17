from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import os, random, string, datetime

# ================= APP =================
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ================= CONFIG =================
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "recuperador-secret")

# 🔴 POSTGRESQL DO RENDER (OBRIGATÓRIO)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
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

# ================= MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))

    reset_code = db.Column(db.String(6))
    reset_expire = db.Column(db.DateTime)

# ================= UTILS =================
def gen_code():
    return "".join(random.choices(string.digits, k=6))

def send_email(to, subject, body):
    if not app.config["MAIL_USERNAME"]:
        return
    msg = Message(subject, recipients=[to], body=body)
    mail.send(msg)

# ================= STATUS =================
@app.route("/")
def status():
    return jsonify(service="Recuperador de Contas Online", status="ok")

# ================= RECUPERAR UTILIZADOR =================
@app.route("/recover/username", methods=["POST"])
def recover_username():
    data = request.json
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado"), 404

    send_email(
        email,
        "Recuperação de Utilizador",
        f"O seu nome de utilizador é: {user.username}"
    )

    return jsonify(status="ok")

# ================= PEDIR CÓDIGO PASSWORD =================
@app.route("/recover/password/request", methods=["POST"])
def recover_password_request():
    data = request.json
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado"), 404

    code = gen_code()
    user.reset_code = code
    user.reset_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    db.session.commit()

    send_email(
        email,
        "Código de Recuperação de Password",
        f"O seu código de recuperação é: {code}\nVálido por 5 minutos."
    )

    return jsonify(status="ok")

# ================= CONFIRMAR NOVA PASSWORD =================
@app.route("/recover/password/confirm", methods=["POST"])
def recover_password_confirm():
    data = request.json
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error"), 404

    if not user.reset_code or user.reset_code != code:
        return jsonify(status="error", msg="Código inválido"), 400

    if user.reset_expire < datetime.datetime.utcnow():
        return jsonify(status="error", msg="Código expirado"), 400

    if check_password_hash(user.password, new_password):
        return jsonify(status="error", msg="Nova password igual à antiga"), 400

    user.password = generate_password_hash(new_password)
    user.reset_code = None
    user.reset_expire = None
    db.session.commit()

    return jsonify(status="ok", msg="Password alterada com sucesso")

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
