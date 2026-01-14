from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor de recuperação ativo"

@app.route("/status")
def status():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
