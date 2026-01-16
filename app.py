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
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]  # 🔧 ALTERADO

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
    print("📧 A enviar email para:", to)  # debug útil
    msg = Message(subject=subject, recipients=[to], body=body)
    mail.send(msg)
    print("✅ Email enviado")

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
  margin:0;height:100vh;display:flex;justify-content:center;align-items:center;
  background:linear-gradient(135deg,#020617,#1e293b);
  font-family:Arial;color:white;
}
.card{
  background:#020617;padding:40px;width:420px;border-radius:18px;
  box-shadow:0 20px 40px rgba(0,0,0,.7);text-align:center;
}
button{
  width:100%;padding:14px;border:none;border-radius:10px;
  font-size:15px;cursor:pointer;margin-top:10px;
}
.pass{background:#2563eb;color:white}
.user{background:#16a34a;color:white}
input{
  width:100%;padding:12px;margin-top:12px;border-radius:8px;
  border:1px solid #334155;
}
.box{display:none;margin-top:20px}
.msg{margin-top:12px;color:#38bdf8}
</style>
</head>
<body>

<div class="card">
  <h2 style="color:#22c55e">Servidor Online ✅</h2>
  <p>Login Google e API ativos.</p>

  <div id="buttonsBox">
    <button class="pass" onclick="showPass()">🔐 Recuperar Palavra-Passe</button>
    <button class="user" onclick="showUser()">👤 Recuperar Utilizador</button>
  </div>

  <!-- PASSWORD -->
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

  <!-- USER -->
  <div id="userBox" class="box">
    <input id="userEmail" placeholder="Email registado">
    <button class="user" onclick="recoverUser()">Recuperar utilizador</button>
    <div class="msg" id="userMsg"></div>
  </div>
</div>

<script>
console.log("JS carregado");

function hideButtons(){
  document.getElementById("buttonsBox").style.display = "none";
}

function showPass(){
  hideButtons();
  document.getElementById("passBox").style.display = "block";
}

function showUser(){
  hideButtons();
  document.getElementById("userBox").style.display = "block";
}

/* ---------- PASSWORD ---------- */

function sendCode(){
  const email = document.getElementById("passEmail").value;
  if(!email){
    document.getElementById("passMsg").innerText = "Introduz o email";
    return;
  }

  fetch("/api/send-reset", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ email: email })
  })
  .then(r => r.json())
  .then(d => {
    document.getElementById("passMsg").innerText = d.msg;
    if(d.status === "ok"){
      document.getElementById("codeBox").style.display = "block";
    }
  })
  .catch(() => {
    document.getElementById("passMsg").innerText = "Erro no servidor";
  });
}

function resetPass(){
  fetch("/api/reset-pass", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      email: document.getElementById("passEmail").value,
      code: document.getElementById("code").value,
      password: document.getElementById("newpass").value
    })
  })
  .then(r => r.json())
  .then(d => {
    document.getElementById("passMsg").innerText = d.msg;
  });
}

/* ---------- USER ---------- */

function recoverUser(){
  const email = document.getElementById("userEmail").value;

  if(!email){
    document.getElementById("userMsg").innerText = "Introduz o email";
    return;
  }

  fetch("/api/recover-user", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ email: email })
  })
  .then(r => r.json())
  .then(d => {
    document.getElementById("userMsg").innerText = d.msg;
  })
  .catch(() => {
    document.getElementById("userMsg").innerText = "Erro ao contactar servidor";
  });
}
</script>

</body>
</html>
"""

# ================= API =================
@app.route("/api/send-reset", methods=["POST"])
def send_reset():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado"), 404

    user.reset_code = gen_code()
    user.reset_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    db.session.commit()

    send_email(email, "Código de recuperação", f"Código: {user.reset_code}")
    return jsonify(status="ok", msg="Código enviado para o email")


@app.route("/api/reset-pass", methods=["POST"])
def reset_pass():
    data = request.get_json()

    user = User.query.filter_by(email=data.get("email")).first()
    if not user or user.reset_code != data.get("code"):
        return jsonify(status="error", msg="Código inválido"), 400

    if datetime.datetime.utcnow() > user.reset_expire:
        return jsonify(status="error", msg="Código expirado"), 400

    user.password = generate_password_hash(data.get("password"))
    user.reset_code = None
    user.reset_expire = None
    db.session.commit()

    return jsonify(status="ok", msg="Password alterada com sucesso")


@app.route("/api/recover-user", methods=["POST"])
def recover_user():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status="error", msg="Email não encontrado"), 404

    send_email(
        email,
        "Utilizador da conta",
        f"O seu utilizador é: {user.username}"
    )

    return jsonify(status="ok", msg="Email enviado com o seu nome de utilizador")

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
# ================= GOOGLE =================
def continuar_google():
    codigo = simpledialog.askstring(
        "Login Google",
        "Cole o código fornecido pelo Google:",
        parent=root
    )
    if not codigo:
        return

    try:
        r = requests.post(f"{SERVER_URL}/google-login",
                          json={"token": codigo}, timeout=5)
        data = r.json()

        if data.get("status") == "ok":
            perfil_app["google_nome"] = data.get("nome", "")
            perfil_app["google_email"] = data.get("email", "")
            perfil_app["nome_app"] = data.get("nome", "Utilizador")

            foto_url = data.get("foto")
            if foto_url:
                try:
                    img_bytes = requests.get(foto_url, timeout=5).content
                    caminho = os.path.join(PASTA_FOTOS, "foto_google.png")
                    with open(caminho, "wb") as f:
                        f.write(img_bytes)
                    perfil_app["foto_google"] = caminho
                except:
                    perfil_app["foto_google"] = None

            tela_dashboard()
        else:
            messagebox.showerror("Erro", "Código inválido ou expirado")
    except:
        messagebox.showerror("Erro", "Servidor indisponível")
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
