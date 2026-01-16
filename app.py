from flask import Flask, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import os, random, string, datetime, uuid

# ================= APP =================
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 🔥 FORÇAR HTTPS ATRÁS DO RENDER (ESSENCIAL)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ================= CONFIG =================
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 👉 POSTGRES DO RENDER (fallback sqlite local)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(BASE_DIR, "users.db")
).replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 🔐 sessões seguras (Render / HTTPS)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
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

    # dados google
    google_name = db.Column(db.String(120))
    google_picture = db.Column(db.String(300))
    provider = db.Column(db.String(20), default="local")

    # token para Tkinter
    google_token = db.Column(db.String(64), unique=True)

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
    return """
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Recuperar Conta</title>
<style>
body{
  margin:0;
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  background:linear-gradient(135deg,#020617,#1e293b);
  font-family:Arial,Helvetica,sans-serif;
  color:white;
}
.card{
  background:#020617;
  padding:40px;
  width:440px;
  border-radius:18px;
  box-shadow:0 20px 40px rgba(0,0,0,.7);
}
h2{color:#22c55e;text-align:center}
p{text-align:center}
table{width:100%;margin-top:25px}
td{padding:10px}
button{
  width:100%;
  padding:14px;
  border:none;
  border-radius:10px;
  font-size:15px;
  cursor:pointer;
}
.pass{background:#2563eb;color:white}
.user{background:#16a34a;color:white}
.box{display:none;margin-top:20px}
input{
  width:100%;
  padding:12px;
  margin-top:10px;
  border-radius:8px;
  border:1px solid #334155;
}
.msg{margin-top:10px;color:#38bdf8}
</style>
</head>
<body>

<div class="card">
  <h2>Servidor Online ✅</h2>
  <p>Login Google e API ativos.</p>

  <table>
    <tr><td><button class="pass" onclick="showPass()">🔐 Recuperar Palavra-Passe</button></td></tr>
    <tr><td><button class="user" onclick="showUser()">👤 Recuperar Utilizador</button></td></tr>
  </table>

  <div id="passBox" class="box">
    <input id="passEmail" placeholder="Email da conta">
    <button class="pass" onclick="sendCode()">Enviar código</button>
    <div id="codeBox" style="display:none">
      <input id="code" placeholder="Código recebido">
      <input id="newpass" type="password" placeholder="Nova password">
      <button class="pass" onclick="resetPass()">Alterar password</button>
    </div>
    <div class="msg" id="passMsg"></div>
  </div>

  <div id="userBox" class="box">
    <input id="userEmail" placeholder="Email registado">
    <button class="user" onclick="recoverUser()">Recuperar utilizador</button>
    <div class="msg" id="userMsg"></div>
  </div>
</div>

<script>
function showPass(){passBox.style.display="block";userBox.style.display="none"}
function showUser(){userBox.style.display="block";passBox.style.display="none"}

function sendCode(){
fetch("/api/send-reset",{method:"POST",headers:{'Content-Type':'application/json'},
body:JSON.stringify({email:passEmail.value})})
.then(r=>r.json()).then(d=>{
passMsg.innerText=d.msg;
if(d.status=="ok") codeBox.style.display="block";
})}

function resetPass(){
fetch("/api/reset-pass",{method:"POST",headers:{'Content-Type':'application/json'},
body:JSON.stringify({email:passEmail.value,code:code.value,password:newpass.value})})
.then(r=>r.json()).then(d=>passMsg.innerText=d.msg)
}

function recoverUser(){
fetch("/api/recover-user",{method:"POST",headers:{'Content-Type':'application/json'},
body:JSON.stringify({email:userEmail.value})})
.then(r=>r.json()).then(d=>userMsg.innerText=d.msg)
}
</script>

</body>
</html>
"""

# ================= RECUPERAR PASSWORD =================
@app.route("/api/send-reset", methods=["POST"])
def send_reset():
    email = request.json.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado")

    user.reset_code = gen_code()
    user.reset_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    db.session.commit()

    send_email(email, "Código de recuperação", f"Código: {user.reset_code}")
    return jsonify(status="ok", msg="Código enviado para o email")

@app.route("/api/reset-pass", methods=["POST"])
def reset_pass():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or user.reset_code != data["code"]:
        return jsonify(status="error", msg="Código inválido")

    if datetime.datetime.utcnow() > user.reset_expire:
        return jsonify(status="error", msg="Código expirado")

    user.password = generate_password_hash(data["password"])
    user.reset_code = None
    user.reset_expire = None
    db.session.commit()

    return jsonify(status="ok", msg="Password alterada com sucesso")

# ================= RECUPERAR UTILIZADOR =================
@app.route("/api/recover-user", methods=["POST"])
def recover_user():
    email = request.json.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado")

    send_email(email, "Utilizador da conta", f"O seu utilizador é: {user.username}")
    return jsonify(status="ok", msg="Email enviado com sucesso")

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
        password=generate_password_hash(data["password"]),
        provider="local"
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

    session["user_id"] = user.id
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
    google_name = info.get("name")
    google_picture = info.get("picture")
    username = google_name or email.split("@")[0]

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            username=username,
            email=email,
            password="google",
            google_name=google_name,
            google_picture=google_picture,
            provider="google"
        )
        db.session.add(user)
    else:
        user.google_name = google_name
        user.google_picture = google_picture
        user.provider = "google"

    # 🔑 token para o Tkinter
    user.google_token = uuid.uuid4().hex

    db.session.commit()
    session["user_id"] = user.id

    return f"""
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Login Google OK</title>
<style>
body {{
  margin: 0;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #020617, #1e293b);
  font-family: Arial, Helvetica, sans-serif;
  color: white;
}}
.box {{
  background: #020617;
  padding: 50px;
  border-radius: 16px;
  max-width: 750px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.7);
}}
h1 {{ font-size: 36px; color: #22c55e; }}
p {{ font-size: 20px; }}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 30px 0;
  font-size: 18px;
}}
th, td {{
  border: 1px solid #334155;
  padding: 14px;
}}
th {{ color: #38bdf8; }}
.code {{
  margin-top: 20px;
  font-size: 22px;
  font-weight: bold;
  padding: 18px;
  border-radius: 10px;
  border: 1px dashed #38bdf8;
  background: #020617;
  word-break: break-all;
}}
.timer {{
  margin-top: 15px;
  font-size: 18px;
  color: #f87171;
}}
</style>
</head>
<body>
<div class="box">
  <h1>Login Google OK ✅</h1>
  <p>Pode voltar para a aplicação</p>

  <table>
    <tr><th>O que fazer</th><th>O que acontece</th></tr>
    <tr><td>Copiar o código</td><td>Login no aplicativo</td></tr>
    <tr><td>Usar no app</td><td>Login automático</td></tr>
    <tr><td>Esperar 5 minutos</td><td>Código expira</td></tr>
    <tr><td>Tentar reutilizar</td><td>Não funciona</td></tr>
  </table>

  <div class="code">Código: {user.google_token}</div>
  <div id="timer" class="timer"></div>
</div>

<script>
let tempo = 300;
function atualizar() {{
  let m = Math.floor(tempo / 60);
  let s = tempo % 60;
  document.getElementById("timer").innerText =
    "⏱️ Código válido por " + m + ":" + s.toString().padStart(2,"0") + " minutos";
  tempo--;
  if (tempo >= 0) setTimeout(atualizar, 1000);
}}
atualizar();
</script>
</body>
</html>
"""

# ================= PERFIL / ME =================
@app.route("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(status="error", msg="Não autenticado"), 401

    user = User.query.get(user_id)

    return jsonify(
        status="ok",
        user={
            "username": user.username,
            "email": user.email,
            "google_name": user.google_name,
            "google_picture": user.google_picture,
            "provider": user.provider
        }
    )

# ================= GOOGLE LOGIN TKINTER =================
@app.route("/google-login", methods=["POST"])
def google_login_tk():
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify(status="error")

    user = User.query.filter_by(google_token=token).first()
    if not user:
        return jsonify(status="error")

    return jsonify(status="ok", nome=user.username, email=user.email)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return jsonify(status="ok")

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
