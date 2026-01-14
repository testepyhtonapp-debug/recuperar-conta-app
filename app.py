from flask import Flask, request

app = Flask(__name__)

# ================== PÁGINA INICIAL ==================
@app.route("/")
def inicio():
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Conta</title>
        <style>
            body {
                background:#fafafa;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }
            .box {
                background:white;
                padding:30px;
                border:1px solid #dbdbdb;
                width:320px;
                text-align:center;
            }
            button {
                width:100%;
                padding:12px;
                margin-top:15px;
                background:#0095f6;
                border:none;
                color:white;
                font-weight:bold;
                border-radius:5px;
                cursor:pointer;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Recuperar conta</h2>
            <button onclick="location.href='/recuperar/password'">Recuperar password</button>
            <button onclick="location.href='/recuperar/utilizador'">Recuperar utilizador</button>
        </div>
    </body>
    </html>
    """

# ================== RECUPERAR PASSWORD ==================
@app.route("/recuperar/password", methods=["GET", "POST"])
def recuperar_password():
    mostrar_form_codigo = False
    email = ""

    if request.method == "POST":
        email = request.form.get("email")
        mostrar_form_codigo = True

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Password</title>
        <style>
            body {{
                background:#fafafa;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }}
            .box {{
                background:white;
                padding:30px;
                border:1px solid #dbdbdb;
                width:320px;
                text-align:center;
            }}
            input {{
                width:100%;
                padding:10px;
                margin:8px 0;
                border-radius:5px;
                border:1px solid #ccc;
            }}
            button {{
                width:100%;
                padding:12px;
                background:#0095f6;
                border:none;
                color:white;
                font-weight:bold;
                border-radius:5px;
                cursor:pointer;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Recuperar password</h3>

            <form method="POST">
                <input type="email" name="email" placeholder="Email registado" required>
                <button type="submit">Enviar código</button>
            </form>

            {"<hr><p>Código enviado para: "+email+"</p>" if mostrar_form_codigo else ""}

            {""
            if not mostrar_form_codigo else
            '''
            <form method="POST" action="/recuperar/password/alterar">
                <input type="text" name="codigo" placeholder="Código recebido" required>
                <input type="password" name="password" placeholder="Nova password" required>
                <button type="submit">Alterar password</button>
            </form>
            '''
            }
        </div>
    </body>
    </html>
    """

@app.route("/recuperar/password/alterar", methods=["POST"])
def alterar_password():
    codigo = request.form.get("codigo")
    password = request.form.get("password")

    return f"""
    <h3>Password alterada com sucesso!</h3>
    <p>Código usado: {codigo}</p>
    """

# ================== RECUPERAR UTILIZADOR ==================
@app.route("/recuperar/utilizador", methods=["GET", "POST"])
def recuperar_utilizador():
    enviado = False
    email = ""

    if request.method == "POST":
        email = request.form.get("email")
        enviado = True

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Utilizador</title>
        <style>
            body {{
                background:#fafafa;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }}
            .box {{
                background:white;
                padding:30px;
                border:1px solid #dbdbdb;
                width:320px;
                text-align:center;
            }}
            input {{
                width:100%;
                padding:10px;
                margin:8px 0;
                border-radius:5px;
                border:1px solid #ccc;
            }}
            button {{
                width:100%;
                padding:12px;
                background:#0095f6;
                border:none;
                color:white;
                font-weight:bold;
                border-radius:5px;
                cursor:pointer;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Recuperar utilizador</h3>
            <form method="POST">
                <input type="email" name="email" placeholder="Email registado" required>
                <button type="submit">Enviar utilizador</button>
            </form>

            {"<p>Utilizador enviado para o email: "+email+"</p>" if enviado else ""}
        </div>
    </body>
    </html>
    """

# ================== START ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
