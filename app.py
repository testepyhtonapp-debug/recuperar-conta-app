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
                background:#121212;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                color:white;
            }
            .box {
                background:#1e1e1e;
                padding:30px;
                border-radius:10px;
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
                border-radius:6px;
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
    email = None

    if request.method == "POST":
        email = request.form.get("email")

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Password</title>
        <style>
            body {{
                background:#121212;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                color:white;
            }}
            .box {{
                background:#1e1e1e;
                padding:30px;
                border-radius:10px;
                width:320px;
                text-align:center;
            }}
            input {{
                width:100%;
                padding:10px;
                margin:8px 0;
                border-radius:6px;
                border:none;
            }}
            button {{
                width:100%;
                padding:12px;
                background:#0095f6;
                border:none;
                color:white;
                font-weight:bold;
                border-radius:6px;
                cursor:pointer;
            }}
            .info {{
                margin:15px 0;
                color:#aaa;
                font-size:14px;
            }}
        </style>
    </head>
    <body>
        <div class="box">

        {""
        if email else
        '''
        <h3>Recuperar password</h3>
        <form method="POST">
            <input type="email" name="email" placeholder="Email registado" required>
            <button type="submit">Enviar código</button>
        </form>
        '''
        }

        {""
        if not email else
        f'''
        <h3>Alterar password</h3>
        <p class="info">Código enviado para:<br>{email}</p>
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
    return """
    <html>
    <head>
        <style>
            body {
                background:#121212;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                color:white;
            }
            .box {
                background:#1e1e1e;
                padding:30px;
                border-radius:10px;
                text-align:center;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Password alterada com sucesso ✅</h3>
        </div>
    </body>
    </html>
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
                background:#121212;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                color:white;
            }}
            .box {{
                background:#1e1e1e;
                padding:30px;
                border-radius:10px;
                width:320px;
                text-align:center;
            }}
            input {{
                width:100%;
                padding:10px;
                margin:8px 0;
                border-radius:6px;
                border:none;
            }}
            button {{
                width:100%;
                padding:12px;
                background:#0095f6;
                border:none;
                color:white;
                font-weight:bold;
                border-radius:6px;
                cursor:pointer;
            }}
            .info {{
                margin-top:15px;
                color:#aaa;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Recuperar utilizador</h3>

            {""
            if enviado else
            '''
            <form method="POST">
                <input type="email" name="email" placeholder="Email registado" required>
                <button type="submit">Enviar</button>
            </form>
            '''
            }

            {""
            if not enviado else
            f'<p class="info">Utilizador enviado para:<br>{email}</p>'
            }
        </div>
    </body>
    </html>
    """

# ================== START ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
