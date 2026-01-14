from flask import Flask, request, render_template_string
import sqlite3
import hashlib
import random
import smtplib
import os
from email.mime.text import MIMEText

app = Flask(__name__)

# ================== CONFIG (SEGURA) ==================
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# ================== DATABASE ==================
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================== HASH ==================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================== EMAIL ==================
def enviar_email(destino, assunto, mensagem):
    msg = MIMEText(mensagem)
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destino

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
        server.send_message(msg)

# ================== HTML ==================
HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Recuperar Conta</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
    margin: 0;
    background: #0f0f0f;
    color: white;
    font-family: Arial;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}
.box {
    background: #1e1e1e;
    padding: 30px;
    border-radius: 16px;
    width: 100%;
    max-width: 400px;
    text-align: center;
}
input, button {
    width: 100%;
    padding: 14px;
    margin: 10px 0;
    border-radius: 10px;
    border: none;
    font-size: 16px;
}
button {
    background: #0a84ff;
    color: white;
    cursor: pointer;
}
a {
    color: #0a84ff;
    text-decoration: none;
}
@media (max-width: 600px) {
    .box { max-width: 95%; }
    input, button { font-size: 20px; padding: 18px; }
}
</style>
</head>

<body>
<div class="box">
<h2>Recuperar conta</h2>

{% if etapa == "menu" %}
    <a href="/password">Recuperar password</a><br><br>
    <a href="/utilizador">Recuperar utilizador</a>
{% endif %}

{% if etapa == "email" %}
<form method="post">
    <input type="email" name="email" placeholder="Email registado" required>
    <button type="submit">Enviar código</button>
</form>
{% endif %}

{% if etapa == "codigo" %}
<p>Código enviado para:<br><b>{{ email }}</b></p>
<form method="post">
    <input type="hidden" name="email" value="{{ email }}">
    <input type="text" name="codigo" placeholder="Código recebido" required>
    <input type="password" name="password" placeholder="Nova password" required>
    <button type="submit">Alterar password</button>
</form>
{% endif %}

{% if etapa == "sucesso" %}
<p>✅ Operação concluída com sucesso</p>
{% endif %}

{% if erro %}
<p style="color:red">{{ erro }}</p>
{% endif %}
</div>
</body>
</html>
"""

# ================== ROTAS ==================
codigos = {}

@app.route("/")
def menu():
    return render_template_string(HTML, etapa="menu")

# -------- PASSWORD --------
@app.route("/password", methods=["GET", "POST"])
def recuperar_password():
    if request.method == "POST":
        email = request.form.get("email")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()

        if not user:
            return render_template_string(HTML, etapa="email", erro="Email não encontrado")

        codigo = str(random.randint(100000, 999999))
        codigos[email] = codigo

        enviar_email(
            email,
            "Código de recuperação",
            f"O seu código de recuperação é: {codigo}"
        )

        return render_template_string(HTML, etapa="codigo", email=email)

    if request.method == "POST" and "codigo" in request.form:
        pass

    return render_template_string(HTML, etapa="email")

@app.route("/password", methods=["POST"])
def confirmar_password():
    email = request.form.get("email")
    codigo = request.form.get("codigo")
    nova = request.form.get("password")

    if codigos.get(email) != codigo:
        return render_template_string(HTML, etapa="codigo", email=email, erro="Código inválido")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hash_password(nova), email)
    )
    conn.commit()
    codigos.pop(email)

    return render_template_string(HTML, etapa="sucesso")

# -------- UTILIZADOR --------
@app.route("/utilizador", methods=["GET", "POST"])
def recuperar_utilizador():
    if request.method == "POST":
        email = request.form.get("email")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE email=?", (email,))
        user = cur.fetchone()

        if not user:
            return render_template_string(HTML, etapa="email", erro="Email não encontrado")

        enviar_email(
            email,
            "Recuperação de utilizador",
            f"O seu utilizador é: {user['username']}"
        )

        return render_template_string(HTML, etapa="sucesso")

    return render_template_string(HTML, etapa="email")

# ================== START ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
