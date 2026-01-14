from flask import Flask, request, render_template_string
import sqlite3
import hashlib
import random
import smtplib
import os
from email.message import EmailMessage

app = Flask(__name__)

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reset_codes (
            email TEXT,
            code TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= EMAIL =================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def enviar_email(destino, assunto, corpo):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = destino
    msg["Subject"] = assunto
    msg.set_content(corpo)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

# ================= HTML =================
HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Recuperar Conta</title>
<style>
body {
    background:#111;
    color:white;
    font-family:Arial;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}
.box {
    background:#1e1e1e;
    padding:30px;
    border-radius:15px;
    width:350px;
    text-align:center;
}
input, button {
    width:100%;
    padding:14px;
    margin-top:10px;
    border-radius:8px;
    border:none;
}
button {
    background:#0a84ff;
    color:white;
    cursor:pointer;
}
</style>
</head>
<body>

<div class="box">
<h2>Recuperar Password</h2>

{% if etapa == "email" %}
<form method="post">
    <input type="hidden" name="acao" value="enviar_codigo">
    <input type="email" name="email" placeholder="Email" required>
    <button>Enviar email</button>
</form>
{% endif %}

{% if etapa == "codigo" %}
<form method="post">
    <input type="hidden" name="acao" value="confirmar">
    <input type="hidden" name="email" value="{{ email }}">
    <input type="text" name="code" placeholder="Código recebido" required>
    <input type="password" name="password" placeholder="Nova password" required>
    <button>Alterar password</button>
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

# ================= ROUTE =================
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        acao = request.form.get("acao")

        # 1️⃣ Enviar código
        if acao == "enviar_codigo":
            email = request.form.get("email")

            c.execute("SELECT * FROM users WHERE email=?", (email,))
            user = c.fetchone()
            if not user:
                return render_template_string(
                    HTML,
                    etapa="resultado",
                    mensagem="Email não encontrado"
                )

            code = str(random.randint(100000, 999999))

            c.execute("DELETE FROM reset_codes WHERE email=?", (email,))
            c.execute(
                "INSERT INTO reset_codes (email, code) VALUES (?,?)",
                (email, code)
            )
            conn.commit()

            enviar_email(
                email,
                "Recuperação de Password",
                f"O teu código de recuperação é: {code}"
            )

            return render_template_string(
                HTML,
                etapa="codigo",
                email=email
            )

        # 2️⃣ Confirmar código + nova password
        if acao == "confirmar":
            email = request.form.get("email")
            code = request.form.get("code")
            password = request.form.get("password")

            c.execute(
                "SELECT * FROM reset_codes WHERE email=? AND code=?",
                (email, code)
            )
            valid = c.fetchone()
            if not valid:
                return render_template_string(
                    HTML,
                    etapa="resultado",
                    mensagem="Código inválido"
                )

            hashed = hashlib.sha256(password.encode()).hexdigest()
            c.execute(
                "UPDATE users SET password=? WHERE email=?",
                (hashed, email)
            )
            c.execute("DELETE FROM reset_codes WHERE email=?", (email,))
            conn.commit()

            return render_template_string(
                HTML,
                etapa="resultado",
                mensagem="Password alterada com sucesso!"
            )

    return render_template_string(HTML, etapa="email")

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
