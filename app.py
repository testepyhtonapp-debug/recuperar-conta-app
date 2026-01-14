from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "status ok"

@app.route("/recuperar")
def recuperar():
    return "Página de recuperação (escolher utilizador ou password)"

@app.route("/recuperar/password")
def recuperar_password():
    return "Recuperação de password"

@app.route("/recuperar/utilizador")
def recuperar_utilizador():
    return "Recuperação de utilizador"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
