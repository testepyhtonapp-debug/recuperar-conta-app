<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <title>Recuperação de Conta</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f2f2f2;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .box {
      background: white;
      padding: 30px;
      width: 320px;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,.2);
    }
    input, button {
      width: 100%;
      padding: 10px;
      margin-top: 10px;
    }
    button {
      cursor: pointer;
    }
    .hidden {
      display: none;
    }
    p {
      text-align: center;
      color: green;
    }
  </style>
</head>
<body>

<div class="box">

  <!-- TELA INICIAL -->
  <div id="home">
    <h2>Recuperar Conta</h2>
    <button onclick="show('user')">Recuperar Utilizador</button>
    <button onclick="show('pass')">Recuperar Password</button>
  </div>

  <!-- RECUPERAR UTILIZADOR -->
  <div id="user" class="hidden">
    <h3>Recuperar Utilizador</h3>
    <input id="userEmail" placeholder="Email">
    <button onclick="recoverUser()">Enviar</button>
    <p id="userMsg"></p>
    <button onclick="show('home')">Voltar</button>
  </div>

  <!-- RECUPERAR PASSWORD -->
  <div id="pass" class="hidden">
    <h3>Recuperar Password</h3>
    <input id="passEmail" placeholder="Email">
    <button onclick="requestCode()">Enviar Código</button>
    <p id="passMsg"></p>
    <button onclick="show('home')">Voltar</button>
  </div>

  <!-- CONFIRMAR PASSWORD -->
  <div id="confirm" class="hidden">
    <h3>Nova Password</h3>
    <input id="code" placeholder="Código">
    <input id="newPass" type="password" placeholder="Nova password">
    <button onclick="confirmPass()">Confirmar</button>
    <p id="confirmMsg"></p>
  </div>

</div>

<script>
const API = "https://recuperadordeconta-app.onrender.com";

function show(id) {
  document.querySelectorAll(".box > div").forEach(d => d.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

async function recoverUser() {
  const email = userEmail.value;
  const r = await fetch(API + "/recover/username", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email})
  });

  userMsg.textContent = r.ok ? "Email enviado com sucesso!" : "Email não encontrado";
}

async function requestCode() {
  const email = passEmail.value;
  const r = await fetch(API + "/recover/password/request", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email})
  });

  if (r.ok) {
    show("confirm");
  } else {
    passMsg.textContent = "Email não encontrado";
  }
}

async function confirmPass() {
  const email = passEmail.value;
  const code = document.getElementById("code").value;
  const new_password = document.getElementById("newPass").value;

  const r = await fetch(API + "/recover/password/confirm", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email, code, new_password})
  });

  confirmMsg.textContent = r.ok ? "Password alterada com sucesso!" : "Erro no código";
}
</script>

</body>
</html>
