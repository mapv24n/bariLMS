// ── Panel lateral: Actividades, Secciones y Sub-secciones ──

import { state } from './state.js';
import { showFormAlert, hideFormAlert } from './utils.js';
import { confirmar } from './modal-confirmar.js';

// ─── Visibilidad del panel ────────────────────────────────────────────────────

export function showSidePanel(mode) {
    state.sidePanelMode = mode;
    document.getElementById('side-panel').style.display = 'block';

    const isActForm = mode === 'crear' || mode === 'editar';
    const isSecForm = mode === 'sec_crear' || mode === 'sec_editar';
    const isSubForm = mode === 'sub_crear' || mode === 'sub_editar';

    document.getElementById('side-crear').style.display = isActForm ? 'block' : 'none';
    const elSec = document.getElementById('side-seccion');
    if (elSec) elSec.style.display = isSecForm ? 'block' : 'none';
    const elSub = document.getElementById('side-subseccion');
    if (elSub) elSub.style.display = isSubForm ? 'block' : 'none';

    if (isActForm) {
        document.getElementById('side-crear-title').textContent = mode === 'editar'
            ? 'Editar actividad de aprendizaje' : 'Crear actividad de aprendizaje';
        document.getElementById('side-crear-btn').textContent = mode === 'editar'
            ? 'Guardar cambios' : 'Aceptar y crear actividad';
    }
    if (isSecForm) {
        document.getElementById('side-sec-title').textContent = mode === 'sec_editar' ? 'Editar sección'    : 'Nueva sección';
        document.getElementById('side-sec-btn').textContent   = mode === 'sec_editar' ? 'Guardar cambios'   : 'Aceptar y agregar';
    }
    if (isSubForm) {
        document.getElementById('side-sub-title').textContent = mode === 'sub_editar' ? 'Editar sub-sección' : 'Nueva sub-sección';
        document.getElementById('side-sub-btn').textContent   = mode === 'sub_editar' ? 'Guardar cambios'    : 'Aceptar y agregar';
    }
}

export function hideSidePanel() {
    state.sidePanelMode = null;
    state.editingActId  = null;
    state.currentSecId  = null;
    state.currentSubId  = null;
    document.getElementById('side-panel').style.display = 'none';
}

// ─── Actividad de aprendizaje ─────────────────────────────────────────────────

export function toggleCrearPanel() {
    if (state.sidePanelMode === 'crear') {
        hideSidePanel();
    } else {
        state.editingActId = null;
        document.getElementById('form-nombre').value     = '';
        document.getElementById('form-desc').value       = '';
        document.getElementById('form-guia-url').value   = '';
        document.getElementById('form-inicio').value     = new Date().toISOString().split('T')[0];
        document.getElementById('form-fin').value        = '';
        document.getElementById('form-nombre-error').style.display = 'none';
        showSidePanel('crear');
    }
}

export function editarActividad(actId) {
    const act = state.actividadesCache.find(a => a.id === actId);
    if (!act) return;
    state.editingActId = actId;
    document.getElementById('form-nombre').value    = act.nombre       || '';
    document.getElementById('form-desc').value      = act.descripcion  || '';
    document.getElementById('form-guia-url').value  = act.guia_url     || '';
    document.getElementById('form-inicio').value    = act.fecha_inicio || '';
    document.getElementById('form-fin').value       = act.fecha_fin    || '';
    document.getElementById('form-nombre-error').style.display = 'none';
    showSidePanel('editar');
}

export async function confirmarCrearActividad() {
    if (state.sidePanelMode === 'editar') { await _confirmarEditarActividad(); return; }

    const nombre = document.getElementById('form-nombre').value.trim();
    if (!nombre) {
        showFormAlert('form-actividad-alert', 'danger', 'El nombre de la actividad es obligatorio.', false);
        document.getElementById('form-nombre').focus();
        return;
    }
    hideFormAlert('form-actividad-alert');

    const formData = new FormData();
    formData.append('nombre',       nombre);
    formData.append('descripcion',  document.getElementById('form-desc').value.trim());
    formData.append('guia_url',     document.getElementById('form-guia-url').value.trim());
    formData.append('fecha_inicio', document.getElementById('form-inicio').value);
    formData.append('fecha_fin',    document.getElementById('form-fin').value);

    try {
        const res  = await fetch(`/api/instructor/actividad-proyecto/${state.selectedActProyId}/aprendizaje/nueva`, {
            method: 'POST', body: formData,
        });
        const data = await res.json();
        if (data.ok) {
            showFormAlert('form-actividad-alert', 'success', `Actividad <strong>${nombre}</strong> creada correctamente.`);
            setTimeout(() => { hideSidePanel(); _dispatch('fases:actividades-refresh'); }, 1200);
        } else {
            showFormAlert('form-actividad-alert', 'danger', data.error || 'No se pudo crear la actividad.', false);
        }
    } catch (e) {
        showFormAlert('form-actividad-alert', 'danger', 'Error de conexión. Intenta de nuevo.', false);
    }
}

async function _confirmarEditarActividad() {
    const nombre = document.getElementById('form-nombre').value.trim();
    if (!nombre) {
        showFormAlert('form-actividad-alert', 'danger', 'El nombre de la actividad es obligatorio.', false);
        document.getElementById('form-nombre').focus();
        return;
    }
    hideFormAlert('form-actividad-alert');

    const formData = new FormData();
    formData.append('nombre',       nombre);
    formData.append('descripcion',  document.getElementById('form-desc').value.trim());
    formData.append('guia_url',     document.getElementById('form-guia-url').value.trim());
    formData.append('fecha_inicio', document.getElementById('form-inicio').value);
    formData.append('fecha_fin',    document.getElementById('form-fin').value);

    try {
        const res  = await fetch(`/api/instructor/actividad-aprendizaje/${state.editingActId}/editar`, {
            method: 'PATCH', body: formData,
        });
        const data = await res.json();
        if (data.ok) {
            showFormAlert('form-actividad-alert', 'success', 'Actividad actualizada correctamente.');
            setTimeout(() => { hideSidePanel(); _dispatch('fases:actividades-refresh'); }, 1200);
        } else {
            showFormAlert('form-actividad-alert', 'danger', data.error || 'No se pudo actualizar la actividad.', false);
        }
    } catch (e) {
        showFormAlert('form-actividad-alert', 'danger', 'Error de conexión. Intenta de nuevo.', false);
    }
}

// ─── Secciones ────────────────────────────────────────────────────────────────

export function abrirCrearSeccion(aaId) {
    state.editingActId = aaId;
    state.currentSecId = null;
    ['sec-nombre', 'sec-url', 'sec-desc', 'sec-inicio', 'sec-fin']
        .forEach(id => { document.getElementById(id).value = ''; });
    showSidePanel('sec_crear');
}

export function abrirEditarSeccion(secId) {
    const sec = state._secData[secId];
    if (!sec) return;
    state.currentSecId = sec.id;
    document.getElementById('sec-nombre').value  = sec.nombre       || '';
    document.getElementById('sec-url').value     = sec.archivo_url  || '';
    document.getElementById('sec-desc').value    = sec.descripcion  || '';
    document.getElementById('sec-inicio').value  = sec.fecha_inicio || '';
    document.getElementById('sec-fin').value     = sec.fecha_fin    || '';
    showSidePanel('sec_editar');
}

export async function guardarSeccion() {
    const nombre = document.getElementById('sec-nombre').value.trim();
    if (!nombre) {
        showFormAlert('form-seccion-alert', 'danger', 'El nombre de la sección es obligatorio.', false);
        return;
    }
    hideFormAlert('form-seccion-alert');

    const payload = {
        nombre,
        archivo_url:  document.getElementById('sec-url').value.trim()   || null,
        descripcion:  document.getElementById('sec-desc').value.trim()   || null,
        fecha_inicio: document.getElementById('sec-inicio').value        || null,
        fecha_fin:    document.getElementById('sec-fin').value           || null,
    };

    try {
        const url = state.sidePanelMode === 'sec_crear'
            ? `/api/instructor/actividad-aprendizaje/${state.editingActId}/seccion/nueva`
            : `/api/instructor/seccion/${state.currentSecId}/editar`;
        const method = state.sidePanelMode === 'sec_crear' ? 'POST' : 'PATCH';

        const res  = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (!res.ok) { showFormAlert('form-seccion-alert', 'danger', `Error del servidor (${res.status}).`, false); return; }
        const data = await res.json();
        if (data.ok) {
            showFormAlert('form-seccion-alert', 'success', state.sidePanelMode === 'sec_crear' ? 'Sección creada correctamente.' : 'Sección actualizada correctamente.');
            setTimeout(() => { hideSidePanel(); _dispatch('fases:actividades-refresh'); }, 1200);
        } else {
            showFormAlert('form-seccion-alert', 'danger', data.error || 'Error al guardar la sección.', false);
        }
    } catch (e) {
        showFormAlert('form-seccion-alert', 'danger', 'Error inesperado: ' + e.message, false);
    }
}

export async function eliminarSeccion(secId) {
    const ok = await confirmar('¿Eliminar esta sección y todo su contenido? Esta acción no se puede deshacer.');
    if (!ok) return;
    const res  = await fetch(`/api/instructor/seccion/${secId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.ok) _dispatch('fases:actividades-refresh');
    else alert(data.error || 'Error al eliminar sección');
}

// ─── Sub-secciones ────────────────────────────────────────────────────────────

export function abrirCrearSubSeccion(secId) {
    state.currentSecId = secId;
    state.currentSubId = null;
    ['sub-nombre', 'sub-url', 'sub-desc', 'sub-inicio', 'sub-fin']
        .forEach(id => { document.getElementById(id).value = ''; });
    showSidePanel('sub_crear');
}

export function abrirEditarSubSeccion(subId) {
    const sub = state._subData[subId];
    if (!sub) return;
    state.currentSecId = sub.id_seccion;
    state.currentSubId = sub.id;
    document.getElementById('sub-nombre').value  = sub.nombre       || '';
    document.getElementById('sub-url').value     = sub.archivo_url  || '';
    document.getElementById('sub-desc').value    = sub.descripcion  || '';
    document.getElementById('sub-inicio').value  = sub.fecha_inicio || '';
    document.getElementById('sub-fin').value     = sub.fecha_fin    || '';
    showSidePanel('sub_editar');
}

export async function guardarSubSeccion() {
    const nombre = document.getElementById('sub-nombre').value.trim();
    if (!nombre) {
        showFormAlert('form-subseccion-alert', 'danger', 'El nombre de la sub-sección es obligatorio.', false);
        return;
    }
    hideFormAlert('form-subseccion-alert');

    const payload = {
        nombre,
        archivo_url:  document.getElementById('sub-url').value.trim()   || null,
        descripcion:  document.getElementById('sub-desc').value.trim()   || null,
        fecha_inicio: document.getElementById('sub-inicio').value        || null,
        fecha_fin:    document.getElementById('sub-fin').value           || null,
    };

    try {
        const url = state.sidePanelMode === 'sub_crear'
            ? `/api/instructor/seccion/${state.currentSecId}/sub-seccion/nueva`
            : `/api/instructor/sub-seccion/${state.currentSubId}/editar`;
        const method = state.sidePanelMode === 'sub_crear' ? 'POST' : 'PATCH';

        const res  = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (!res.ok) { showFormAlert('form-subseccion-alert', 'danger', `Error del servidor (${res.status}).`, false); return; }
        const data = await res.json();
        if (data.ok) {
            showFormAlert('form-subseccion-alert', 'success', state.sidePanelMode === 'sub_crear' ? 'Sub-sección creada correctamente.' : 'Sub-sección actualizada correctamente.');
            setTimeout(() => { hideSidePanel(); _dispatch('fases:actividades-refresh'); }, 1200);
        } else {
            showFormAlert('form-subseccion-alert', 'danger', data.error || 'Error al guardar la sub-sección.', false);
        }
    } catch (e) {
        showFormAlert('form-subseccion-alert', 'danger', 'Error inesperado: ' + e.message, false);
    }
}

export async function eliminarSubSeccion(subId) {
    const ok = await confirmar('¿Eliminar esta sub-sección? Esta acción no se puede deshacer.');
    if (!ok) return;
    const res  = await fetch(`/api/instructor/sub-seccion/${subId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.ok) _dispatch('fases:actividades-refresh');
    else alert(data.error || 'Error al eliminar sub-sección');
}

// ─── Delegación de eventos (sobre #actividades-lista) ─────────────────────────

export function initSidePanelDelegate() {
    const lista = document.getElementById('actividades-lista');
    if (!lista) return;

    lista.addEventListener('click', e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const { action, id } = btn.dataset;

        if (action === 'editar-actividad')   editarActividad(id);
        if (action === 'crear-seccion')      abrirCrearSeccion(id);
        if (action === 'editar-seccion')     abrirEditarSeccion(id);
        if (action === 'eliminar-seccion')   eliminarSeccion(id);
        if (action === 'crear-subseccion')   abrirCrearSubSeccion(id);
        if (action === 'editar-subseccion')  abrirEditarSubSeccion(id);
        if (action === 'eliminar-subseccion') eliminarSubSeccion(id);
    });

    // Tecla Enter en el campo nombre de actividad
    document.getElementById('form-nombre')?.addEventListener('keydown', e => {
        if (e.key === 'Enter') confirmarCrearActividad();
    });
}

// ─── Helper interno ───────────────────────────────────────────────────────────

function _dispatch(eventName) {
    document.dispatchEvent(new CustomEvent(eventName));
}
