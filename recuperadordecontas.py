from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import os, random, string, datetime

# ================= APP =================
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ================= CONFIG =================
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "recover-secret")

# PostgreSQL do Render (MESMA DB do app principal)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ================= EMAIL =================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

db = SQLAlchemy(app)
mail = Mail(app)

# ================= MODEL (IGUAL AO APP PRINCIPAL) =================
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))

    reset_code = db.Column(db.String(6))
    reset_expire = db.Column(db.DateTime)

# ================= UTILS =================
def gerar_codigo():
    return "".join(random.choices(string.digits, k=6))

def enviar_email(dest, assunto, texto):
    if not app.config["MAIL_USERNAME"]:
        return
    msg = Message(assunto, recipients=[dest], body=texto)
    mail.send(msg)

# ================= HOME =================
@app.route("/")
def home():
    return jsonify(
        status="ok",
        service="Recuperador de Contas Online"
    )

# ================= RECUPERAR UTILIZADOR =================
@app.route("/recover-username", methods=["POST"])
def recover_username():
    email = request.json.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado")

    enviar_email(
        email,
        "Recuperação de Utilizador",
        f"O seu nome de utilizador do aplicativo é: {user.username}"
    )

    return jsonify(status="ok", msg="Utilizador enviado para o email")

# ================= RECUPERAR PASSWORD (ETAPA 1) =================
@app.route("/recover-password", methods=["POST"])
def recover_password():
    email = request.json.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado")

    codigo = gerar_codigo()
    user.reset_code = codigo
    user.reset_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    db.session.commit()

    enviar_email(
        email,
        "Código de recuperação de password",
        f"O seu código para alterar a palavra-passe é: {codigo}\n\n"
        "Este código é válido por 10 minutos."
    )

    return jsonify(status="ok", msg="Código enviado para o email")

# ================= ALTERAR PASSWORD (ETAPA 2) =================
@app.route("/reset-password", methods=["POST"])
def reset_password():
    codigo = request.json.get("code")
    nova_password = request.json.get("password")

    if not codigo or not nova_password:
        return jsonify(status="error", msg="Dados incompletos")

    user = User.query.filter_by(reset_code=codigo).first()
    if not user:
        return jsonify(status="error", msg="Código inválido")

    if user.reset_expire < datetime.datetime.utcnow():
        return jsonify(status="error", msg="Código expirado")

    user.password = generate_password_hash(nova_password)
    user.reset_code = None
    user.reset_expire = None

    db.session.commit()

    return jsonify(
        status="ok",
        msg="✔ Palavra-passe alterada com sucesso"
    )

# ================= START =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

