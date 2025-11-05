let token = localStorage.getItem("token");
let userData = null;

// --------------------------
// UTILS
// --------------------------
function showLoading() {
    document.getElementById("loading").classList.remove("hidden");
}

// --------------------------
// Admin panel actions
// --------------------------
async function cargarPanelAdmin() {
    // populate role filter with available groups
    try {
        const rolesSelect = document.getElementById('filter_role');
        if (rolesSelect) {
            // fetch groups from API - we don't have groups endpoint, derive from users
            const resp = await fetch('/api/users/?page=1', {headers: {Authorization: 'Bearer ' + token}});
            const json = await resp.json();
            const items = json.results || json;
            const groups = new Set();
            (items || []).forEach(u => { (u.groups || []).forEach(g => groups.add(g)); });
            rolesSelect.innerHTML = '<option value="">Todos</option>' + Array.from(groups).map(g => `<option value="${g}">${g}</option>`).join('');
        }
    } catch (err) {
        console.warn('No se pudieron cargar roles', err);
    }
    // initial load
    buscarUsuarios();
    cargarRespaldos();
    cargarHistorial();
    // auditoria will load on tab click
}

async function buscarUsuarios() {
    const table = document.querySelector('#adminUsersTable tbody');
    if (!table) return;
    table.innerHTML = '<tr><td colspan="5">Cargando...</td></tr>';
    try {
        const resp = await fetch('/api/users/?page=1', {headers: {Authorization: 'Bearer ' + token}});
        const data = await resp.json();
        const items = data.results || data;
        const filterName = (document.getElementById('filter_user').value || '').toLowerCase();
        const filterEmail = (document.getElementById('filter_email').value || '').toLowerCase();
        const filterRole = (document.getElementById('filter_role').value || '').toLowerCase();
        const filtered = (items || []).filter(u => {
            const name = (u.username || '') + ' ' + (u.first_name || '') + ' ' + (u.last_name || '');
            const okName = !filterName || name.toLowerCase().includes(filterName);
            const okEmail = !filterEmail || (u.email || '').toLowerCase().includes(filterEmail);
            const groups = (u.groups || []).map(g => g.toLowerCase());
            const okRole = !filterRole || groups.includes(filterRole);
            return okName && okEmail && okRole;
        });
        if (filtered.length === 0) table.innerHTML = '<tr><td colspan="5">No se encontraron usuarios</td></tr>';
        else table.innerHTML = filtered.map(u => `
            <tr>
              <td>${u.username}</td>
              <td>${(u.groups || []).join(', ')}</td>
              <td>${u.email || ''}</td>
              <td>${u.is_active ? 'Activo' : 'Inactivo'}</td>
              <td>
                <a class="btn btn-sm btn-danger me-2" href="/admin/auth/user/${u.id}/change/">Editar</a>
                <button class="btn btn-sm btn-dark" onclick="disableUser(${u.id})">Deshabilitar</button>
              </td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Error cargando usuarios', err);
        table.innerHTML = '<tr><td colspan="5">Error cargando usuarios</td></tr>';
    }
}

function limpiarFiltrosUsuarios() {
    document.getElementById('filter_user').value = '';
    document.getElementById('filter_role').value = '';
    document.getElementById('filter_email').value = '';
    buscarUsuarios();
}

async function disableUser(id) {
    if (!confirm('¿Confirma deshabilitar este usuario?')) return;
    try {
        const res = await fetch(`/api/users/${id}/disable/`, {method: 'POST', headers: {Authorization: 'Bearer ' + token}});
        if (res.ok) {
            Swal.fire({icon: 'success', title: 'Usuario deshabilitado'});
            buscarUsuarios();
        } else {
            const data = await res.json();
            Swal.fire({icon: 'error', title: 'Error', text: data.detail || 'No se pudo deshabilitar'});
        }
    } catch (err) {
        console.error(err);
        Swal.fire({icon: 'error', title: 'Error', text: 'Error en la solicitud'});
    }
}

async function filtrarAuditoria() {
    const tbody = document.querySelector('#auditoriaTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5">Cargando...</td></tr>';
    try {
        const resp = await fetch('/api/logs/?page=1', {headers: {Authorization: 'Bearer ' + token}});
        const json = await resp.json();
        const items = json.results || json;
        const userFilter = (document.getElementById('aud_user').value || '').toLowerCase();
        const actionFilter = (document.getElementById('aud_action').value || '').toLowerCase();
        const filtered = (items || []).filter(l => {
            const user = (l.usuario && l.usuario.username) || '';
            const accion = l.accion || '';
            return (!userFilter || user.toLowerCase().includes(userFilter)) && (!actionFilter || accion.toLowerCase().includes(actionFilter));
        });
        tbody.innerHTML = filtered.map(l => `
            <tr>
              <td>${l.fecha}</td>
              <td>${l.usuario ? (l.usuario.username || '') : ''}</td>
              <td>${l.usuario ? (l.usuario.email || '') : ''}</td>
              <td>${l.accion}</td>
              <td>${l.detalle || ''}</td>
            </tr>
        `).join('') || '<tr><td colspan="5">No hay registros</td></tr>';
    } catch (err) {
        console.error('Error cargando auditoria', err);
        tbody.innerHTML = '<tr><td colspan="5">Error al cargar auditoría</td></tr>';
    }
}

async function cargarRespaldos() {
    const tbody = document.querySelector('#respaldosTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="4">Cargando...</td></tr>';
    try {
        const resp = await fetch('/api/archivos/?page=1', {headers: {Authorization: 'Bearer ' + token}});
        const json = await resp.json();
        const items = json.results || json;
        tbody.innerHTML = (items || []).map(a => `
            <tr>
              <td>${a.id}</td>
              <td>${a.fecha_carga}</td>
              <td>${a.estado_validacion}</td>
              <td><a class="text-danger" href="#">RESTAURAR</a></td>
            </tr>
        `).join('') || '<tr><td colspan="4">No hay respaldos</td></tr>';
    } catch (err) {
        console.error('Error cargando respaldos', err);
        tbody.innerHTML = '<tr><td colspan="4">Error cargando respaldos</td></tr>';
    }
}

async function crearRespaldo() {
    // placeholder: real backup should be implemented server-side
    Swal.fire({icon: 'info', title: 'Crear respaldo', text: 'Esta acción debe ser implementada en el backend.'});
}

async function cargarHistorial() {
    const tbody = document.querySelector('#historialTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5">Cargando...</td></tr>';
    try {
        const resp = await fetch('/api/archivos/?page=1', {headers: {Authorization: 'Bearer ' + token}});
        const json = await resp.json();
        const items = json.results || json;
        tbody.innerHTML = (items || []).map(a => `
            <tr>
              <td>${a.nombre_archivo || a.id}</td>
              <td>${a.usuario ? (a.usuario.username || '') : ''}</td>
              <td>${a.estado_validacion}</td>
              <td><a href="#">VER DETALLES</a></td>
            </tr>
        `).join('') || '<tr><td colspan="5">No hay cargas</td></tr>';
    } catch (err) {
        console.error('Error cargando historial', err);
        tbody.innerHTML = '<tr><td colspan="5">Error cargando historial</td></tr>';
    }
}

// hook tab shown to load auditoria on demand
document.addEventListener('DOMContentLoaded', function() {
    const tabAud = document.getElementById('tab-auditoria');
    if (tabAud) tabAud.addEventListener('shown.bs.tab', function() { filtrarAuditoria(); });
});

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

    // --------------------------
    // Role panel loaders (use existing API endpoints)
    // --------------------------
    async function cargarPanelAdmin() {
        const admin = document.getElementById('adminPanel');
        if (!admin) return;
        admin.querySelector('.card-body').innerHTML = '<h3 class="mb-3 text-danger"><i class="fas fa-user-shield me-2"></i>Panel Administrador</h3><p>Cargando...</p>';
        try {
            // obtener conteo de calificaciones
            const calResp = await fetch('/api/calificaciones/?page=1');
            const calJson = await calResp.json();
            const calCount = calJson.count ?? (Array.isArray(calJson) ? calJson.length : 0);

            // obtener conteo de usuarios
            const usersResp = await fetch('/api/users/?page=1');
            const usersJson = await usersResp.json();
            const usersCount = usersJson.count ?? (Array.isArray(usersJson) ? usersJson.length : 0);

            admin.querySelector('.card-body').innerHTML = `
                <h3 class="mb-3 text-danger"><i class="fas fa-user-shield me-2"></i>Panel Administrador</h3>
                <div class="row">
                  <div class="col-md-4"><div class="p-3 border rounded"><strong>${calCount}</strong><div class="text-muted">Calificaciones</div></div></div>
                  <div class="col-md-4"><div class="p-3 border rounded"><strong>${usersCount}</strong><div class="text-muted">Usuarios</div></div></div>
                  <div class="col-md-4"><a href="/admin/" class="btn btn-outline-secondary mt-1">Ir al Admin</a></div>
                </div>
            `;
        } catch (err) {
            console.error('Error cargando admin panel', err);
            admin.querySelector('.card-body').innerHTML = '<p class="text-danger">Error al cargar datos del panel administrativo</p>';
        }
    }

    async function cargarPanelCorredor() {
        const panel = document.getElementById('corredorPanel');
        if (!panel) return;
        panel.querySelector('.card-body').innerHTML = '<h3 class="mb-3 text-primary"><i class="fas fa-briefcase me-2"></i>Panel Corredor</h3><p>Cargando...</p>';
        try {
            // obtener últimas 5 calificaciones del usuario
            const resp = await fetch('/api/calificaciones/?page=1');
            const json = await resp.json();
            const items = json.results || json;
            const listHtml = (items.slice ? items.slice(0,5) : []).map(i => `
                <tr>
                  <td>${i.id}</td>
                  <td>${i.monto_factor}</td>
                  <td>${i.fecha_emision}</td>
                  <td>${i.estado ? i.estado : ''}</td>
                </tr>
            `).join('');

            panel.querySelector('.card-body').innerHTML = `
                <h3 class="mb-3 text-primary"><i class="fas fa-briefcase me-2"></i>Panel Corredor</h3>
                <p>Acceso rápido para crear y revisar calificaciones.</p>
                <div class="table-responsive"><table class="table table-sm"><thead><tr><th>ID</th><th>Monto</th><th>F. Emisión</th><th>Estado</th></tr></thead><tbody>${listHtml}</tbody></table></div>
            `;
        } catch (err) {
            console.error('Error cargando corredor panel', err);
            panel.querySelector('.card-body').innerHTML = '<p class="text-danger">Error al cargar datos</p>';
        }
    }

    async function cargarPanelSupervisor() {
        const panel = document.getElementById('supervisorPanel');
        if (!panel) return;
        panel.querySelector('.card-body').innerHTML = '<h3 class="mb-3 text-warning"><i class="fas fa-user-tie me-2"></i>Panel Supervisor</h3><p>Cargando...</p>';
        try {
            // mostramos las calificaciones recientes para revisar
            const resp = await fetch('/api/calificaciones/?page=1');
            const json = await resp.json();
            const items = json.results || json;
            const pending = (items.filter ? items.filter(i => i.estado && String(i.estado).toLowerCase().includes('pend')) : []).slice(0,5);
            const listHtml = pending.map(i => `
                <tr>
                  <td>${i.id}</td>
                  <td>${i.monto_factor}</td>
                  <td>${i.fecha_emision}</td>
                  <td>${i.estado}</td>
                </tr>
            `).join('') || '<tr><td colspan="4">No hay items pendientes</td></tr>';

            panel.querySelector('.card-body').innerHTML = `
                <h3 class="mb-3 text-warning"><i class="fas fa-user-tie me-2"></i>Panel Supervisor</h3>
                <p>Revisión de calificaciones pendientes.</p>
                <div class="table-responsive"><table class="table table-sm"><thead><tr><th>ID</th><th>Monto</th><th>F. Emisión</th><th>Estado</th></tr></thead><tbody>${listHtml}</tbody></table></div>
            `;
        } catch (err) {
            console.error('Error cargando supervisor panel', err);
            panel.querySelector('.card-body').innerHTML = '<p class="text-danger">Error al cargar datos</p>';
        }
    }
