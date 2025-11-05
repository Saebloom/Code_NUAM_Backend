let token = localStorage.getItem("token");
let userData = null;

// --------------------------
// UTILS
// --------------------------
function showLoading() {
    document.getElementById("loading").classList.remove("hidden");
}

function hideLoading() {
    document.getElementById("loading").classList.add("hidden");
}

function validateEmail(email) {
    const re = /^[a-zA-Z0-9._-]+@nuam\.cl$/;
    return re.test(email.toLowerCase());
}

function validateRut(rut) {
    const re = /^[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9kK]$/;
    return re.test(rut);
}

function hideAllCards() {
    document.getElementById("loginCard").classList.add("hidden");
    document.getElementById("registerCard").classList.add("hidden");
    document.getElementById("forgotCard").classList.add("hidden");
    document.getElementById("appCard").classList.add("hidden");
}

// --------------------------
// NAVIGATION
// --------------------------
function showLogin() {
    hideAllCards();
    document.getElementById("loginCard").classList.remove("hidden");
}

function showRegister() {
    hideAllCards();
    document.getElementById("registerCard").classList.remove("hidden");
}

function showForgotPassword() {
    hideAllCards();
    document.getElementById("forgotCard").classList.remove("hidden");
}

// --------------------------
// LOGIN
// --------------------------
async function login() {
    try {
        showLoading();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        if (!username || !password) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor ingrese email y contraseña'
            });
            return;
        }

        if (!validateEmail(username)) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor ingrese un email corporativo válido (@nuam.cl)'
            });
            return;
        }

        const res = await fetch("/api/auth/token/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });

        const data = await res.json();

        if (res.ok) {
            token = data.access;
            localStorage.setItem("token", token);
            await getUserInfo();
            mostrarApp();
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error de acceso',
                text: 'Email o contraseña incorrectos'
            });
        }
    } catch (error) {
        console.error(error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al intentar iniciar sesión'
        });
    } finally {
        hideLoading();
    }
}

// --------------------------
// REGISTER
// --------------------------
async function register() {
    try {
        showLoading();

        const nombres = document.getElementById("reg_nombres").value;
        const apellidos = document.getElementById("reg_apellidos").value;
        const rut = document.getElementById("reg_rut").value;
        const email = document.getElementById("reg_email").value;
        const genero = document.getElementById("reg_genero").value;
        const telefono = document.getElementById("reg_telefono").value;
        const direccion = document.getElementById("reg_direccion").value;

        // Validaciones
        if (!nombres || !apellidos || !rut || !email || !genero || !telefono || !direccion) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor complete todos los campos'
            });
            return;
        }

        if (!validateEmail(email)) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor ingrese un email corporativo válido (@nuam.cl)'
            });
            return;
        }

        if (!validateRut(rut)) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor ingrese un RUT válido (Ej: 12.345.678-9)'
            });
            return;
        }

        const res = await fetch("/api/register/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                nombres, apellidos, rut, email,
                genero, telefono, direccion
            })
        });

        if (res.ok) {
            Swal.fire({
                icon: 'success',
                title: '¡Registro exitoso!',
                text: 'Se ha enviado un correo de confirmación. Por favor revise su bandeja de entrada.'
            }).then(() => {
                showLogin();
            });
        } else {
            const data = await res.json();
            Swal.fire({
                icon: 'error',
                title: 'Error en el registro',
                text: data.detail || 'Error al procesar el registro'
            });
        }
    } catch (error) {
        console.error(error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al procesar el registro'
        });
    } finally {
        hideLoading();
    }
}

// --------------------------
// RECOVER PASSWORD
// --------------------------
async function recoverPassword() {
    try {
        showLoading();

        const lastPassword = document.getElementById("forgot_lastpass").value;
        const email = document.getElementById("forgot_email").value;
        const rut = document.getElementById("forgot_rut").value;

        if (!lastPassword || !email || !rut) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor complete todos los campos'
            });
            return;
        }

        if (!validateEmail(email)) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor ingrese un email corporativo válido (@nuam.cl)'
            });
            return;
        }

        if (!validateRut(rut)) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor ingrese un RUT válido (Ej: 12.345.678-9)'
            });
            return;
        }

        const res = await fetch("/api/recover-password/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                last_password: lastPassword,
                email: email,
                rut: rut
            })
        });

        if (res.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Solicitud enviada',
                text: 'Se ha enviado una notificación a soporte. Pronto recibirá instrucciones en su email.'
            }).then(() => {
                showLogin();
            });
        } else {
            const data = await res.json();
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.detail || 'Error al procesar la solicitud'
            });
        }
    } catch (error) {
        console.error(error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al procesar la solicitud'
        });
    } finally {
        hideLoading();
    }
}

async function getUserInfo() {
    try {
        const res = await fetch("/api/users/me/", {
            headers: {"Authorization": "Bearer " + token}
        });
        userData = await res.json();
        document.getElementById("userInfo").innerHTML = `
            <i class="fas fa-user me-2"></i>${userData.username}
        `;
        // Show role-specific UI
        showRoleUI(userData);
    } catch (error) {
        console.error('Error getting user info:', error);
    }
}

// --------------------------
// LOGOUT
// --------------------------
function logout() {
    Swal.fire({
        title: '¿Cerrar sesión?',
        text: "¿Está seguro que desea cerrar la sesión?",
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, cerrar sesión',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            localStorage.removeItem("token");
            token = null;
            userData = null;
            showLogin();
        }
    });
}

// --------------------------
// MOSTRAR APP
// --------------------------
async function mostrarApp() {
    hideAllCards();
    document.getElementById("appCard").classList.remove("hidden");
    await Promise.all([
        cargarInstrumentos(),
        cargarMercados(),
        cargarEstados(),
        listarCalificaciones()
    ]);
    // after loading content, make sure role UI is applied
    if (userData) showRoleUI(userData);
}

// Inicializar app
if (token) {
    getUserInfo().then(() => mostrarApp());
} else {
    showLogin();
}

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

// --------------------------
// ROLE UI
// --------------------------
function showRoleUI(user) {
    // hide all role panels first
    const admin = document.getElementById('adminPanel');
    const corredor = document.getElementById('corredorPanel');
    const supervisor = document.getElementById('supervisorPanel');
    if (admin) admin.classList.add('hidden');
    if (corredor) corredor.classList.add('hidden');
    if (supervisor) supervisor.classList.add('hidden');

    if (!user) return;

    // Decide role by flags/groups
    const groups = (user.groups || []).map(g => g.toLowerCase());
    if (user.is_superuser) {
        if (admin) admin.classList.remove('hidden');
    } else if (groups.includes('corredor') || groups.includes('brokers') || groups.includes('broker')) {
        if (corredor) corredor.classList.remove('hidden');
    } else if (user.is_staff || groups.includes('supervisor') || groups.includes('supervisores')) {
        if (supervisor) supervisor.classList.remove('hidden');
    } else {
        // default: show corredor panel for regular users
        if (corredor) corredor.classList.remove('hidden');
    }
}
