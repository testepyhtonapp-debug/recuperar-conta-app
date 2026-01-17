from flask import Flask, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix
import os, uuid

# ================= APP =================
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 🔒 ESSENCIAL PARA RENDER (HTTPS atrás de proxy)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ================= CONFIG =================
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ================= INIT =================
db = SQLAlchemy(app)
oauth = OAuth(app)

# ================= GOOGLE OAUTH =================
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "openid email profile"},
)

# ================= MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    google_name = db.Column(db.String(120))
    google_picture = db.Column(db.String(300))
    provider = db.Column(db.String(20), default="google")

    google_token = db.Column(db.String(64), unique=True)

# ================= HOME =================
@app.route("/")
def home():
    return "<h2>Servidor Login Google Online ✅</h2>"

# ================= LOGIN GOOGLE =================
@app.route("/login/google")
def login_google():
    # 🔑 Redirect URI AUTOMÁTICO (HTTPS do Render)
    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google/callback")
def google_callback():
    token = google.authorize_access_token()
    info = google.get("userinfo").json()

    email = info["email"]
    name = info.get("name")
    picture = info.get("picture")
    username = name or email.split("@")[0]

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            username=username,
            email=email,
            google_name=name,
            google_picture=picture,
            provider="google"
        )
        db.session.add(user)
    else:
        user.google_name = name
        user.google_picture = picture

    # 🔑 Token para o app Tkinter
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
img {{
  border-radius: 50%;
  width: 90px;
  margin-bottom: 15px;
}}
</style>
</head>
<body>
<div class="box">
  <img src="{picture}">
  <h1>Login Google OK ✅</h1>
  <p>{name} ({email})</p>

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

# ================= TOKEN PARA TKINTER =================
@app.route("/google-login", methods=["POST"])
def google_login_token():
    token = request.json.get("token")

    user = User.query.filter_by(google_token=token).first()
    if not user:
        return jsonify(status="error")

    return jsonify(
        status="ok",
        username=user.username,
        email=user.email,
        name=user.google_name,
        picture=user.google_picture
    )

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
