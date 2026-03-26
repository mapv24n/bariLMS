// ── Guías de Actividades de Aprendizaje ──

import { state } from './state.js';
import { escapar, showFormAlert, hideFormAlert } from './utils.js';
import { confirmar } from './modal-confirmar.js';

let _sortableGuiasAprendizaje = null;

// ─── Carga y render ───────────────────────────────────────────────────────────

export async function cargarGuiasAprendizaje(apId) {
    const res  = await fetch(`/api/instructor/actividad-proyecto/${apId}/guias-aprendizaje`);
    const data = await res.json();
    state.guiasAprendizajeCache = data.guias || [];
    renderGuiasAprendizaje(state.guiasAprendizajeCache);

    // Informar que se cargaron las guías para que el árbol evalúe desbloqueo
    document.dispatchEvent(new CustomEvent('fases:evaluar-desbloqueo'));
}

export function renderGuiasAprendizaje(guias) {
    const container = document.getElementById('guias-aprendizaje-lista');
    if (!guias || guias.length === 0) {
        container.innerHTML = '';
        if (_sortableGuiasAprendizaje) { _sortableGuiasAprendizaje.destroy(); _sortableGuiasAprendizaje = null; }
        return;
    }

    let html = '<ul class="list-group list-group-flush mb-2" id="guias-aprendizaje-sortable-list">';
    guias.forEach(g => {
        const nombre = escapar(g.nombre || 'Guía sin nombre');
        const url    = escapar(g.url    || '');
        const desc   = escapar(g.descripcion || '');
        html += `
        <li class="list-group-item p-2" data-id="${g.id}">
            <div class="d-flex align-items-center" style="gap:6px;">
                <i class="fas fa-grip-vertical text-muted guia-handle"></i>
                <div style="flex:1; min-width:0;">
                    <a href="${url}" target="_blank" class="text-sena font-weight-bold small">${nombre}</a>
                    ${g.descripcion ? `<div class="text-muted small mt-1">${desc}</div>` : ''}
                </div>
                <button class="btn btn-sm btn-link text-warning" data-action="abrir-editar-guia-aprendizaje" data-id="${g.id}">
                    <i class="fas fa-edit fa-sm"></i>
                </button>
                <button class="btn btn-sm btn-link text-danger ml-1" data-action="eliminar-guia-aprendizaje" data-id="${g.id}">
                    <i class="fas fa-trash fa-sm"></i>
                </button>
            </div>
            <div id="guia-edit-form-${g.id}" class="guia-edit-form mt-2" style="display:none;">
                <div id="guia-edit-alert-${g.id}" class="alert mb-2" role="alert"
                     style="display:none; font-size:.82rem; padding:8px 12px;"></div>
                <div class="guia-edit-group">
                    <label class="guia-edit-label">Nombre</label>
                    <input type="text" class="guia-edit-input" id="guia-edit-nombre-${g.id}"
                           placeholder="Nombre de la guía" value="${nombre}">
                </div>
                <div class="guia-edit-group">
                    <label class="guia-edit-label">Enlace (URL)</label>
                    <input type="url" class="guia-edit-input" id="guia-edit-url-${g.id}"
                           placeholder="https://..." value="${url}">
                </div>
                <div class="guia-edit-group">
                    <label class="guia-edit-label">Descripción</label>
                    <textarea class="guia-edit-input" id="guia-edit-desc-${g.id}" rows="2"
                              placeholder="Descripción opcional...">${desc}</textarea>
                </div>
                <div style="display:flex; gap:6px;">
                    <button class="btn btn-success btn-sm py-1 px-3"
                            data-action="guardar-guia-aprendizaje" data-id="${g.id}">
                        <i class="fas fa-save mr-1"></i>Guardar
                    </button>
                    <button class="btn btn-outline-secondary btn-sm py-1 px-3"
                            data-action="cancelar-editar-guia-aprendizaje" data-id="${g.id}">
                        Cancelar
                    </button>
                </div>
            </div>
        </li>`;
    });
    html += '</ul>';
    container.innerHTML = html;
    _initSortableGuias();
}



function _initSortableGuias() {
    const ul = document.getElementById('guias-aprendizaje-sortable-list');
    if (_sortableGuiasAprendizaje) _sortableGuiasAprendizaje.destroy();
    _sortableGuiasAprendizaje = new Sortable(ul, {
        handle: '.guia-handle',
        animation: 150,
        ghostClass: 'bg-light',
        onEnd: async () => {
            const orden = Array.from(ul.querySelectorAll('li[data-id]'))
                .map(li => parseInt(li.dataset.id));
            await fetch(`/api/instructor/actividad-proyecto/${state.selectedActProyId}/guias/orden`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ orden }),
            });
        },
    });
}

// ─── Acciones ─────────────────────────────────────────────────────────────────

export function toggleFormGuiaAprendizaje() {
    const form    = document.getElementById('form-guia-aprendizaje');
    const visible = form.style.display !== 'none';
    form.style.display = visible ? 'none' : 'block';
    if (!visible) {
        document.getElementById('guia-aprendizaje-nombre').value   = '';
        document.getElementById('guia-aprendizaje-archivo').value  = '';
        document.getElementById('guia-aprendizaje-url').value      = '';
        hideFormAlert('form-guia-aprendizaje-alert');
    }
}

export async function subirGuiaAprendizaje() {
    const fileInput = document.getElementById('guia-aprendizaje-archivo');
    const urlInput  = document.getElementById('guia-aprendizaje-url');

    if (!fileInput.files.length && !urlInput.value.trim()) {
        showFormAlert('form-guia-aprendizaje-alert', 'danger', 'Debes subir un archivo o ingresar un enlace.', false);
        return;
    }
    hideFormAlert('form-guia-aprendizaje-alert');

    const formData = new FormData();
    formData.append('nombre', document.getElementById('guia-aprendizaje-nombre').value.trim());
    formData.append('guia_url', urlInput.value.trim());
    if (fileInput.files.length > 0) formData.append('guia_archivo', fileInput.files[0]);

    try {
        const res  = await fetch(`/api/instructor/actividad-proyecto/${state.selectedActProyId}/guias-aprendizaje/nueva`, {
            method: 'POST', body: formData,
        });
        const data = await res.json();
        if (data.ok) {
            showFormAlert('form-guia-aprendizaje-alert', 'success', 'Guía subida correctamente.');
            setTimeout(() => {
                toggleFormGuiaAprendizaje();
                cargarGuiasAprendizaje(state.selectedActProyId);
                document.dispatchEvent(new CustomEvent('fases:tree-refresh'));
            }, 1200);
        } else {
            showFormAlert('form-guia-aprendizaje-alert', 'danger', data.error || 'No se pudo subir la guía.', false);
        }
    } catch {
        showFormAlert('form-guia-aprendizaje-alert', 'danger', 'Error de conexión. Intenta de nuevo.', false);
    }
}


async function _eliminarGuiasAprendizaje(guiaId) {
    const ok = await confirmar('¿Eliminar esta guía? Esta acción no se puede deshacer.');
    if (!ok) return;
    const res  = await fetch(`/api/instructor/guia-actividad-proyecto/${guiaId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.ok) {
        await cargarGuiasAprendizaje(state.selectedActProyId);
        document.dispatchEvent(new CustomEvent('fases:tree-refresh'));
    }
}

async function _guardarGuiasAprendizaje(guiaId) {
    const nombre      = document.getElementById(`guia-edit-nombre-${guiaId}`).value.trim();
    const url         = document.getElementById(`guia-edit-url-${guiaId}`).value.trim();
    const descripcion = document.getElementById(`guia-edit-desc-${guiaId}`).value.trim();

    if (!url) {
        showFormAlert(`guia-edit-alert-${guiaId}`, 'danger', 'El enlace es obligatorio.', false);
        return;
    }
    hideFormAlert(`guia-edit-alert-${guiaId}`);

    try {
        const res  = await fetch(`/api/instructor/guia-actividad-proyecto/${guiaId}/editar`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, url, descripcion }),
        });
        const data = await res.json();
    if (data.ok) await cargarGuiasAprendizaje(state.selectedActProyId);
        else showFormAlert(`guia-edit-alert-${guiaId}`, 'danger', data.error || 'Error al guardar.', false);
    } catch (e) {
        showFormAlert(`guia-edit-alert-${guiaId}`, 'danger', 'Error inesperado: ' + e.message, false);
    }
}

function _abrirEditarGuiasAprendizaje(guiaId) {
    document.querySelectorAll('[id^="guia-edit-form-"]').forEach(el => {
        if (el.id !== `guia-edit-form-${guiaId}`) el.style.display = 'none';
    });
    document.getElementById(`guia-edit-form-${guiaId}`).style.display = 'block';
}

function _cancelarEditarGuiasAprendizaje(guiaId) {
    document.getElementById(`guia-edit-form-${guiaId}`).style.display = 'none';
}

// ─── Delegación de eventos (sobre #guias-lista) ───────────────────────────────

export function initGuiasDelegate() {
    const lista = document.getElementById('guias-aprendizaje-lista');
    if (!lista) return;

    lista.addEventListener('click', async e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const { action, id } = btn.dataset;

        // Delegate should map:
        if (action === 'abrir-editar-guia-aprendizaje')    _abrirEditarGuiasAprendizaje(id);
        if (action === 'cancelar-editar-guia-aprendizaje') _cancelarEditarGuiasAprendizaje(id);
        if (action === 'guardar-guia-aprendizaje')         await _guardarGuiasAprendizaje(id);
        if (action === 'eliminar-guia-aprendizaje')        await _eliminarGuiasAprendizaje(id);
                
    });
}
