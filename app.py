from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "status ok"

@app.route("/recuperar")
def recuperar():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Recuperar Conta</title>
        <style>
            body {
                background-color: #fafafa;
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
                text-align: center;
                width: 300px;
            }
            h2 {
                margin-bottom: 20px;
            }
            a {
                display: block;
                margin: 10px 0;
                padding: 12px;
                background: #0095f6;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
            a:hover {
                background: #007cd6;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Recuperar conta</h2>
            <a href="/recuperar/password">Recuperar password</a>
            <a href="/recuperar/utilizador">Recuperar utilizador</a>
        </div>
    </body>
    </html>
    """

@app.route("/recuperar/password")
def recuperar_password():
    return "Página de recuperação de password (próximo passo)"

@app.route("/recuperar/utilizador")
def recuperar_utilizador():
    return "Página de recuperação de utilizador (próximo passo)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
