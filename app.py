from flask import Flask, request, render_template_string, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# ================= DATABASE (SERVIDOR) =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    email TEXT,
    nascimento TEXT
)
""")
conn.commit()

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================= CÓDIGOS TEMP =================
codigos = {}  # email -> codigo

# ================= HTML =================
HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Recuperar Conta</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; }
        body {
            margin: 0;
            background: linear-gradient(135deg, #0f0f0f, #1c1c1c);
            color: white;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
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
        @media (max-width: 600px) {
            input, button { font-size: 20px; padding: 18px; }
        }
    </style>
</head>
<body>
<div class="box">
    <h2>Recuperar conta</h2>

    {% if etapa == "email" %}
    <form method="post">
        <p>Introduz o email registado</p>
        <input type="email" name="email" required>
        <button>Enviar código</button>
    </form>
    {% endif %}

    {% if etapa == "codigo" %}
    <p>Código enviado para:<br><b>{{ email }}</b></p>
    <form method="post">
        <input type="hidden" name="email" value="{{ email }}">
        <input name="codigo" placeholder="Código recebido" required>
        <input type="password" name="password" placeholder="Nova password" required>
        <button>Alterar password</button>
    </form>
    {% endif %}

    {% if etapa == "erro" %}
    <p style="color:red;">{{ msg }}</p>
    {% endif %}

    {% if etapa == "sucesso" %}
    <p>✅ Password alterada com sucesso</p>
    {% endif %}
</div>
</body>
</html>
"""

# ================= SITE RECUPERAÇÃO =================
@app.route("/", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":

        if "codigo" in request.form:
            email = request.form["email"]
            codigo = request.form["codigo"]
            nova = hash_password(request.form["password"])

            if codigos.get(email) == codigo:
                cursor.execute(
                    "UPDATE users SET password=? WHERE email=?",
                    (nova, email)
                )
                conn.commit()
                codigos.pop(email)
                return render_template_string(HTML, etapa="sucesso")

            return render_template_string(HTML, etapa="erro", msg="Código inválido")

        email = request.form["email"]
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if not cursor.fetchone():
            return render_template_string(HTML, etapa="erro", msg="Email não encontrado")

        codigos[email] = "1234"  # simulado
        return render_template_string(HTML, etapa="codigo", email=email)

    return render_template_string(HTML, etapa="email")

# ================= API LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    )
    return jsonify(
        status="ok" if cursor.fetchone() else "erro",
        msg="Login inválido"
    )

# ================= API REGISTO =================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    try:
        cursor.execute(
            "INSERT INTO users VALUES (?,?,?,?)",
            (
                data["username"],
                data["password"],
                data["email"],
                data["nascimento"]
            )
        )
        conn.commit()
        return jsonify(status="ok")
    except:
        return jsonify(status="erro", msg="Utilizador já existe")

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
