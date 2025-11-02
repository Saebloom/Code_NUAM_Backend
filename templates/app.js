let token = localStorage.getItem("token");

// --------------------------
// LOGIN
// --------------------------
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/api/auth/token/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const data = await res.json();

    if (res.ok) {
        token = data.access;
        localStorage.setItem("token", token);
        mostrarApp();
    } else {
        document.getElementById("loginMsg").innerText = "Usuario o contraseña incorrectos";
    }
}

// --------------------------
// LOGOUT
// --------------------------
function logout() {
    localStorage.removeItem("token");
    token = null;
    document.getElementById("appCard").classList.add("hidden");
    document.getElementById("loginCard").classList.remove("hidden");
}

// --------------------------
// MOSTRAR APP
// --------------------------
function mostrarApp() {
    document.getElementById("loginCard").classList.add("hidden");
    document.getElementById("appCard").classList.remove("hidden");
    listarCalificaciones();
}

if (token) mostrarApp();

// --------------------------
// CREAR CALIFICACION
// --------------------------
async function crearCalificacion() {
    const payload = {
        monto_factor: document.getElementById("c_monto").value,
        fecha_emision: document.getElementById("c_emision").value,
        fecha_pago: document.getElementById("c_pago").value,
        instrumento: document.getElementById("c_instrumento").value,
        mercado: document.getElementById("c_mercado").value,
        estado: document.getElementById("c_estado").value
    };

    const res = await fetch("/api/calificaciones/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.ok) {
        document.getElementById("createMsg").innerText = "✅ Calificación creada (ID " + data.id + ")";
        listarCalificaciones();
    } else {
        document.getElementById("createMsg").innerText = "❌ Error: " + JSON.stringify(data);
    }
}

// --------------------------
// LISTAR CALIFICACIONES
// --------------------------
async function listarCalificaciones() {
    const res = await fetch("/api/calificaciones/", {
        headers: {"Authorization": "Bearer " + token}
    });

    const data = await res.json();

    const tbody = document.querySelector("#tablaCalificaciones tbody");
    tbody.innerHTML = "";

    data.forEach(reg => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${reg.id}</td>
            <td>${reg.monto_factor}</td>
            <td>${reg.fecha_emision}</td>
            <td>${reg.fecha_pago}</td>
            <td><button onclick="editarCalificacion(${reg.id})">Editar</button></td>
            <td><button onclick="borrarCalificacion(${reg.id})" style="background:#dc3545">Eliminar</button></td>
        `;

        tbody.appendChild(tr);
    });
}

// --------------------------
// EDITAR CALIFICACION
// --------------------------
async function editarCalificacion(id) {
    const nuevoMonto = prompt("Nuevo monto:");

    if (!nuevoMonto) return;

    const res = await fetch(`/api/calificaciones/${id}/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({monto_factor: nuevoMonto})
    });

    if (res.ok) listarCalificaciones();
    else alert("Error al editar");
}

// --------------------------
// BORRAR CALIFICACION
// --------------------------
async function borrarCalificacion(id) {
    if (!confirm("¿Seguro de borrar?")) return;

    const res = await fetch(`/api/calificaciones/${id}/`, {
        method: "DELETE",
        headers: {"Authorization": "Bearer " + token}
    });

    if (res.ok) listarCalificaciones();
    else alert("Error al eliminar");
}
