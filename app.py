from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os, random, string, datetime

app = Flask(__name__)

# ================= CONFIG =================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

# ================= EMAIL =================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

db = SQLAlchemy(app)
mail = Mail(app)

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

# ================= HOME / FRONTEND =================
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Recuperar Conta</title>
<style>
body { font-family: Arial; background:#f4f4f4; padding:40px }
.card { background:#fff; padding:20px; max-width:420px; margin:auto; border-radius:8px }
button { width:100%; padding:10px; margin-top:10px; cursor:pointer }
input { width:100%; padding:8px; margin-top:5px }
.hidden { display:none }
#msg { margin-top:15px; font-weight:bold }
</style>
</head>
<body>

<div class="card">
<h2>Recuperar Conta</h2>

<button onclick="show('user')">👤 Recuperar Utilizador</button>
<button onclick="show('pass')">🔐 Recuperar Palavra-passe</button>

<div id="user" class="hidden">
<h3>Recuperar utilizador</h3>
<input id="userEmail" placeholder="Email">
<button onclick="recoverUsername()">Enviar</button>
</div>

<div id="pass" class="hidden">
<h3>Recuperar palavra-passe</h3>
<input id="passEmail" placeholder="Email">
<button onclick="sendCode()">Enviar código</button>

<input id="code" placeholder="Código recebido">
<input id="newPass" type="password" placeholder="Nova password">
<button onclick="resetPass()">Alterar password</button>
</div>

<p id="msg"></p>
</div>

<script>
function show(id){
 document.getElementById('user').classList.add('hidden')
 document.getElementById('pass').classList.add('hidden')
 document.getElementById(id).classList.remove('hidden')
 document.getElementById('msg').innerText = ''
}

function recoverUsername(){
 fetch('/recover-username',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({email:userEmail.value})
 }).then(r=>r.json()).then(d=>{
  msg.innerText = d.msg || 'Email enviado'
 })
}

function sendCode(){
 fetch('/recover-password',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({email:passEmail.value})
 }).then(r=>r.json()).then(d=>{
  msg.innerText = d.msg || 'Código enviado'
 })
}

function resetPass(){
 fetch('/reset-password',{
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({
    email:passEmail.value,
    code:code.value,
    new_password:newPass.value
  })
 }).then(r=>r.json()).then(d=>{
  msg.innerText = d.msg || 'Password alterada'
 })
}
</script>

</body>
</html>
""")

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

# ================= RECOVER USERNAME =================
@app.route("/recover-username", methods=["POST"])
def recover_username():
    email = request.json["email"]
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify(status="error", msg="Email não encontrado")

    send_email(
        email,
        "Recuperar Utilizador",
        f"O teu nome de utilizador é: {user.username}"
    )

    return jsonify(status="ok", msg="Email enviado")

# ================= RECOVER PASSWORD =================
@app.route("/recover-password", methods=["POST"])
def recover_password():
    email = request.json["email"]
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify(status="error", msg="Email não encontrado")

    code = gen_code()
    user.reset_code = code
    user.reset_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    db.session.commit()

    send_email(
        email,
        "Código de recuperação",
        f"O teu código é: {code}"
    )

    return jsonify(status="ok", msg="Código enviado")

# ================= RESET PASSWORD =================
@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or user.reset_code != data["code"]:
        return jsonify(status="error", msg="Código inválido")

    if datetime.datetime.utcnow() > user.reset_expire:
        return jsonify(status="error", msg="Código expirado")

    user.password = generate_password_hash(data["new_password"])
    user.reset_code = None
    user.reset_expire = None
    db.session.commit()

    return jsonify(status="ok", msg="Password alterada")

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
