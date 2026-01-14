from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Recuperar Conta</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        * {
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

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
            box-shadow: 0 0 30px rgba(0,0,0,0.6);
        }

        h2 {
            margin-bottom: 20px;
        }

        .info {
            margin-bottom: 15px;
            font-size: 15px;
            color: #bbb;
        }

        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border-radius: 10px;
            border: none;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 14px;
            margin-top: 15px;
            border: none;
            border-radius: 10px;
            background: #0a84ff;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #006edc;
        }

        /* 📱 APENAS TELEMÓVEL */
        @media (max-width: 600px) {
            .box {
                max-width: 95%;
                padding: 35px;
            }

            h2 {
                font-size: 28px;
            }

            .info {
                font-size: 18px;
            }

            input {
                font-size: 20px;
                padding: 18px;
            }

            button {
                font-size: 20px;
                padding: 18px;
            }
        }
    </style>
</head>

<body>
    <div class="box">
        <h2>Recuperar conta</h2>

        {% if etapa == "email" %}
            <form method="post">
                <div class="info">Introduz o email registado</div>
                <input type="email" name="email" required placeholder="email@exemplo.com">
                <button type="submit">Enviar código</button>
            </form>
        {% endif %}

        {% if etapa == "codigo" %}
            <div class="info">Código enviado para:<br><b>{{ email }}</b></div>
            <form method="post">
                <input type="hidden" name="email" value="{{ email }}">
                <input type="text" name="codigo" required placeholder="Código recebido">
                <input type="password" name="password" required placeholder="Nova password">
                <button type="submit">Alterar password</button>
            </form>
        {% endif %}

        {% if etapa == "sucesso" %}
            <div class="info">✅ Password alterada com sucesso</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        if "codigo" in request.form:
            return render_template_string(HTML, etapa="sucesso")
        else:
            email = request.form.get("email")
            return render_template_string(HTML, etapa="codigo", email=email)

    return render_template_string(HTML, etapa="email")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
