from flask import Flask, request, render_template_string
import sqlite3
import hashlib
import random
import smtplib
import os
from email.mime.text import MIMEText

app = Flask(__name__)

# ================= CONFIG =================
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# ================= DATABASE =================
def get_db():
    return sqlite3.connect("users.db", check_same_thread=False)

# ================= EMAIL =================
def enviar_email(destino, assunto, mensagem):
    msg = MIMEText(mensagem)
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destino

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
        server.send_message(msg)

# ================= HTML =================
HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Recuperar Conta</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body{
    margin:0;
    background:#111;
    color:white;
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:100vh;
    font-family:Arial;
}
.box{
    background:#1e1e1e;
    padding:30px;
    border-radius:16px;
    width:100%;
    max-width:400px;
    text-align:center;
}
button,input{
    width:100%;
    padding:14px;
    margin-top:12px;
    border:none;
    border-radius:10px;
    font-size:16px;
}
button{
    background:#0a84ff;
    color:white;
    cursor:pointer;
}
button:hover{background:#006edc;}
@media (max-width:600px){
    .box{padding:40px;}
    h2{font-size:28px;}
    button,input{font-size:20px;padding:18px;}
}
</style>
</head>

<body>
<div class="box">
<h2>Recuperar conta</h2>

{% if etapa == "inicio" %}
<form method="post">
<button name="acao" value="password">Recuperar password</button>
<button name="acao" value="utilizador">Recuperar utilizador</button>
</form>
{% endif %}

{% if etapa == "email" %}
<form method="post">
<input type="hidden" name="acao" value="{{ acao }}">
<input type="email" name="email" placeholder="Email registado" required>
<button type="submit">Enviar código</button>
</form>
{% endif %}

{% if etapa == "codigo" %}
<p>Código enviado para:<br><b>{{ email }}</b></p>
<form method="post">
<input type="hidden" name="acao" value="{{ acao }}">
<input type="hidden" name="email" value="{{ email }}">
<input type="text" name="codigo" placeholder="Código recebido" required>

{% if acao == "password" %}
<input type="password" name="password" placeholder="Nova password" required>
{% endif %}

<button type="submit">Confirmar</button>
</form>
{% endif %}

{% if etapa == "sucesso" %}
<p>✅ Operação concluída com sucesso</p>
{% endif %}

{% if erro %}
<p style="color:#ff5c5c">{{ erro }}</p>
{% endif %}
</div>
</body>
</html>
"""

# ================= ROUTE =================
codigos = {}

@app.route("/", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":

        acao = request.form.get("acao")

        # escolher ação
        if acao in ["password", "utilizador"] and "email" not in request.form:
            return render_template_string(HTML, etapa="email", acao=acao)

        email = request.form.get("email")
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template_string(
                HTML, etapa="email", acao=acao, erro="Email não encontrado"
            )

        # enviar código
        if "codigo" not in request.form:
            codigo = str(random.randint(100000, 999999))
            codigos[email] = codigo

            enviar_email(
                email,
                "Código de recuperação",
                f"O seu código é: {codigo}"
            )

            return render_template_string(
                HTML, etapa="codigo", email=email, acao=acao
            )

        # confirmar código
        if request.form.get("codigo") != codigos.get(email):
            return render_template_string(
                HTML, etapa="codigo", email=email, acao=acao, erro="Código inválido"
            )

        if acao == "password":
            nova = hashlib.sha256(
                request.form.get("password").encode()
            ).hexdigest()

            cursor.execute(
                "UPDATE users SET password=? WHERE email=?",
                (nova, email)
            )
            conn.commit()

        return render_template_string(HTML, etapa="sucesso")

    return render_template_string(HTML, etapa="inicio")

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
