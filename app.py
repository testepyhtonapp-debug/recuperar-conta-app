from flask import Flask, request, render_template_string
import sqlite3
import hashlib
import random

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

init_db()  # 🔥 ISTO EVITA O ERRO 500

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
<h2>Recuperar Conta</h2>

{% if etapa == "menu" %}
<form method="post">
    <button name="acao" value="password">Recuperar Password</button>
    <button name="acao" value="username">Recuperar Utilizador</button>
</form>
{% endif %}

{% if etapa == "email_password" %}
<form method="post">
    <input type="hidden" name="acao" value="email_password">
    <input type="email" name="email" placeholder="Email" required>
    <button>Enviar</button>
</form>
{% endif %}

{% if etapa == "email_username" %}
<form method="post">
    <input type="hidden" name="acao" value="email_username">
    <input type="email" name="email" placeholder="Email" required>
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

# ================= ROUTE =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        acao = request.form.get("acao")
        email = request.form.get("email")

        conn = get_db()
        cursor = conn.cursor()

        if acao == "password":
            return render_template_string(HTML, etapa="email_password")

        if acao == "username":
            return render_template_string(HTML, etapa="email_username")

        if acao == "email_password":
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                return render_template_string(HTML, etapa="resultado", mensagem="Email não encontrado")

            nova_pass = str(random.randint(100000, 999999))
            hashed = hashlib.sha256(nova_pass.encode()).hexdigest()
            cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed, email))
            conn.commit()

            return render_template_string(
                HTML,
                etapa="resultado",
                mensagem=f"Nova password temporária: {nova_pass}"
            )

        if acao == "email_username":
            cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if not user:
                return render_template_string(HTML, etapa="resultado", mensagem="Email não encontrado")

            return render_template_string(
                HTML,
                etapa="resultado",
                mensagem=f"O teu utilizador é: {user['username']}"
            )

    return render_template_string(HTML, etapa="menu")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
