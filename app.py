from flask import Flask, request

app = Flask(__name__)

# ================== PÁGINA INICIAL ==================
@app.route("/")
def inicio():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Conta</title>
        <style>
            body {
                background: #fafafa;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 30px;
                border: 1px solid #dbdbdb;
                width: 320px;
                text-align: center;
            }
            button {
                width: 100%;
                padding: 12px;
                margin-top: 15px;
                background: #0095f6;
                border: none;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background: #007cd6;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Recuperar conta</h2>
            <button onclick="location.href='/recuperar/password'">
                Recuperar password
            </button>
            <button onclick="location.href='/recuperar/utilizador'">
                Recuperar utilizador
            </button>
        </div>
    </body>
    </html>
    """

# ================== RECUPERAR PASSWORD ==================
@app.route("/recuperar/password")
def recuperar_password():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Password</title>
        <style>
            body {
                background: #fafafa;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 30px;
                border: 1px solid #dbdbdb;
                width: 320px;
                text-align: center;
            }
            input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #0095f6;
                border: none;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Recuperar password</h3>
            <form method="POST" action="/recuperar/password/enviar">
                <input type="email" name="email" placeholder="Email registado" required>
                <button type="submit">Enviar código</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/recuperar/password/enviar", methods=["POST"])
def enviar_password():
    email = request.form.get("email")
    return f"""
    <h3>Código enviado para o email:</h3>
    <p>{email}</p>
    """

# ================== RECUPERAR UTILIZADOR ==================
@app.route("/recuperar/utilizador")
def recuperar_utilizador():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Utilizador</title>
        <style>
            body {
                background: #fafafa;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 30px;
                border: 1px solid #dbdbdb;
                width: 320px;
                text-align: center;
            }
            input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #0095f6;
                border: none;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Recuperar utilizador</h3>
            <form method="POST" action="/recuperar/utilizador/enviar">
                <input type="email" name="email" placeholder="Email registado" required>
                <button type="submit">Enviar utilizador</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/recuperar/utilizador/enviar", methods=["POST"])
def enviar_utilizador():
    email = request.form.get("email")
    return f"""
    <h3>Utilizador associado ao email:</h3>
    <p>{email}</p>
    """

# ================== START ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
