from flask import Flask, request, jsonify, render_template_string
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= EMAIL =================
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def enviar_email(destino, assunto, mensagem):
    msg = MIMEText(mensagem)
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destino

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
        server.send_message(msg)

# ================= API =================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users VALUES (?,?,?)",
            (data["username"], data["password"], data["email"])
        )
        conn.commit()
        return jsonify(status="ok")
    except:
        return jsonify(status="erro", msg="Utilizador ou email já existe")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    )

    if cursor.fetchone():
        return jsonify(status="ok")
    return jsonify(status="erro", msg="Dados incorretos")

# ================= HTML =================
HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Recuperar Conta</title>
<style>
body{background:#111;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh}
.box{background:#1e1e1e;padding:30px;border-radius:15px;width:350px;text-align:center}
input,button{width:100%;padding:14px;margin-top:10px;border-radius:8px;border:none}
button{background:#0a84ff;color:white;cursor:pointer}
</style>
</head>
<body>
<div class="box">
<h2>Recuperar Conta</h2>

{% if etapa == "menu" %}
<form method="post">
<button name="acao" value="password">Recuperar Password</button>
<button name="acao" value="username">Recuperar Utilizador</button>
</form>
{% endif %}

{% if etapa == "email" %}
<form method="post">
<input type="hidden" name="acao" value="{{ tipo }}">
<input type="email" name="email" required placeholder="Email">
<button>Enviar</button>
</form>
{% endif %}

{% if etapa == "resultado" %}
<p>{{ mensagem }}</p>
<a href="/">Voltar</a>
{% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        acao = request.form.get("acao")
        email = request.form.get("email")

        conn = get_db()
        cursor = conn.cursor()

        if acao in ("password", "username"):
            return render_template_string(HTML, etapa="email", tipo=acao)

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template_string(
                HTML, etapa="resultado", mensagem="Email não encontrado"
            )

        if acao == "password":
            nova = str(random.randint(100000, 999999))
            hashed = hashlib.sha256(nova.encode()).hexdigest()
            cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed, email))
            conn.commit()

            enviar_email(
                email,
                "Recuperação de Password",
                f"A tua nova password temporária é: {nova}"
            )

            return render_template_string(
                HTML, etapa="resultado",
                mensagem="📧 Password enviada para o teu email"
            )

        if acao == "username":
            enviar_email(
                email,
                "Recuperação de Utilizador",
                f"O teu utilizador é: {user['username']}"
            )

            return render_template_string(
                HTML, etapa="resultado",
                mensagem="📧 Utilizador enviado para o teu email"
            )

    return render_template_string(HTML, etapa="menu")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
