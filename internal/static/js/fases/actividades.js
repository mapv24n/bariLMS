// ── Actividades de Aprendizaje ──

import { state, sortableInstances } from './state.js';
import { escapar, formatFecha, destroySortable } from './utils.js';
import { renderSecciones, initSortableSecciones, initSortableSubSecciones } from './secciones.js';
import { confirmar } from './modal-confirmar.js';

// ─── Carga y render ───────────────────────────────────────────────────────────

export async function cargarActividades() {
    document.getElementById('act-loading').style.display = 'block';
    document.getElementById('actividades-lista').innerHTML = '';

    const res  = await fetch(`/api/instructor/actividad-proyecto/${state.selectedActProyId}/actividades-aprendizaje`);
    const data = await res.json();

    document.getElementById('act-loading').style.display = 'none';
    renderActividades(data.actividades);
}

export function renderActividades(actividades) {
    state.actividadesCache = actividades || [];
    const container = document.getElementById('actividades-lista');
    destroySortable('actividades');

    if (!actividades || actividades.length === 0) {
        container.innerHTML = `
        <div class="empty-state py-4">
            <i class="fas fa-tasks fa-2x mb-2"></i>
            <p class="mb-1">No hay actividades de aprendizaje creadas.</p>
            <p class="small mb-0">Usa el botón <strong>Crear actividad de aprendizaje</strong> para agregar la primera.</p>
        </div>`;
        return;
    }

    let html = '<div class="accordion" id="accordionActividades">';
    actividades.forEach(act => {
        const inicioFmt = act.fecha_inicio ? formatFecha(act.fecha_inicio) : null;
        const finFmt    = act.fecha_fin    ? formatFecha(act.fecha_fin)    : null;
        const colId     = `collapseAct${act.id}`;
        const headId    = `headingAct${act.id}`;

        const badgeFin = finFmt
            ? `<span class="badge badge-light border" id="badge-fin-${act.id}">
                   <i class="fas fa-calendar-times mr-1 text-warning"></i>Fin: ${finFmt}
                   <button class="btn btn-sm btn-link p-0 ml-1" style="font-size:.9em;line-height:1;"
                           data-action="editar-fecha-fin" data-id="${act.id}" data-fecha="${act.fecha_fin || ''}">
                       <i class="fas fa-edit text-warning"></i>
                   </button>
               </span>`
            : `<button class="btn btn-sm btn-outline-warning py-0 px-2" style="font-size:.75rem;"
                       data-action="editar-fecha-fin" data-id="${act.id}" data-fecha="">
                   <i class="fas fa-calendar-plus mr-1"></i>Agregar fecha fin
               </button>`;

        const badgeEvidencia = act.evidencia_id
            ? `<span class="badge badge-success py-1 px-2" style="font-size:.78rem;">
                   <i class="fas fa-check-circle mr-1"></i>Evidencia activa
               </span>`
            : `<button class="btn btn-outline-warning btn-sm border-0" style="font-size:.75rem;"
                       data-action="activar-evidencia" data-id="${act.id}">
                   <i class="fas fa-plus-circle mr-1"></i>Activar evidencia
               </button>`;

        html += `
        <div class="card mb-2 shadow-sm border-0 actividad-card" data-id="${act.id}" style="padding:0;">
            <div class="card-header bg-white py-2" id="${headId}">
                <div class="d-flex align-items-center" style="gap:6px;">
                    <i class="fas fa-grip-vertical act-drag-handle text-muted"
                       title="Arrastrar para reordenar"
                       style="cursor:grab; font-size:.9em; flex-shrink:0; padding:4px 2px;"></i>
                    <button class="btn btn-link text-left text-dark font-weight-bold text-decoration-none p-0 d-flex align-items-center"
                            type="button" data-toggle="collapse" data-target="#${colId}"
                            aria-expanded="false" style="flex:1;">
                        <i class="fas fa-chevron-down mr-2 text-sena" style="font-size:0.8rem;"></i>
                        ${escapar(act.nombre)}
                    </button>
                </div>
            </div>
            <div id="${colId}" class="collapse" aria-labelledby="${headId}" data-parent="#accordionActividades">
                <div class="card-body bg-light p-3">
                    <div class="d-flex justify-content-between align-items-start mb-3 flex-wrap" style="gap:8px;">
                        <div style="flex:1; min-width:0;">
                            ${act.descripcion ? `<div class="small text-gray-700 mb-2">${escapar(act.descripcion)}</div>` : ''}
                            <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:.8em;">
                                ${inicioFmt ? `<span class="badge badge-light border"><i class="fas fa-calendar-alt mr-1 text-sena"></i>Inicio: ${inicioFmt}</span>` : ''}
                                ${badgeFin}
                                ${act.guia_url ? `<a href="${act.guia_url}" target="_blank" class="badge badge-success border text-white"><i class="fas fa-link mr-1"></i>Guía / Recurso</a>` : ''}
                            </div>
                        </div>
                        <div style="flex-shrink:0; display:flex; gap:6px;">
                            ${badgeEvidencia}
                            <button class="btn btn-outline-secondary btn-sm border-0" style="font-size:.75rem;"
                                    data-action="editar-actividad" data-id="${act.id}">
                                <i class="fas fa-edit mr-1"></i>Editar
                            </button>
                            <button class="btn btn-outline-danger btn-sm border-0" style="font-size:.75rem;"
                                    data-action="eliminar-actividad" data-id="${act.id}">
                                <i class="fas fa-trash mr-1"></i>Eliminar
                            </button>
                            <button class="btn btn-outline-primary btn-sm border-0" style="font-size:.75rem;"
                                    data-action="crear-seccion" data-id="${act.id}">
                                <i class="fas fa-plus mr-1"></i>Nueva Sección
                            </button>
                        </div>
                    </div>
                    <div id="secciones-act-${act.id}">
                        ${renderSecciones(act.secciones, act.id)}
                    </div>
                </div>
            </div>
        </div>`;
    });
    html += '</div>';
    container.innerHTML = html;

    const acordeon = document.getElementById('accordionActividades');
    if (acordeon) {
        const s = new Sortable(acordeon, {
            handle: '.act-drag-handle',
            animation: 150,
            ghostClass: 'bg-light',
            onEnd: async () => {
                const orden = Array.from(acordeon.querySelectorAll('.actividad-card[data-id]'))
                    .map(c => parseInt(c.dataset.id));
                await fetch(`/api/instructor/actividad-proyecto/${state.selectedActProyId}/aprendizaje/orden`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ orden }),
                });
            },
        });
        sortableInstances.set('actividades', s);
    }

    actividades.forEach(act => {
        initSortableSecciones(act.id);
        if (act.secciones) act.secciones.forEach(sec => initSortableSubSecciones(sec.id));
    });
}

// ─── Acciones de actividad ────────────────────────────────────────────────────

export async function activarEvidencia(actId) {
    const res  = await fetch(`/api/instructor/actividad/${actId}/evidencia`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ descripcion: '' }),
    });
    const data = await res.json();
    if (data.ok) await cargarActividades();
}

export async function editarFechaFin(actId, fechaActual) {
    const nueva = prompt('Nueva fecha de fin (AAAA-MM-DD):', fechaActual || '');
    if (nueva === null) return;
    const val = nueva.trim();
    if (val && !/^\d{4}-\d{2}-\d{2}$/.test(val)) {
        alert('Formato incorrecto. Usa AAAA-MM-DD');
        return;
    }
    const res  = await fetch(`/api/instructor/actividad-aprendizaje/${actId}/fecha-fin`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_fin: val || null }),
    });
    const data = await res.json();
    if (data.ok) await cargarActividades();
}

export async function eliminarActividad(actId) {
    const ok = await confirmar('¿Eliminar esta actividad de aprendizaje y todo su contenido? Esta acción no se puede deshacer.');
    if (!ok) return;
    const res  = await fetch(`/api/instructor/actividad-aprendizaje/${actId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.ok) await cargarActividades();
    else alert(data.error || 'Error al eliminar la actividad');
}

// ─── Delegación de eventos ────────────────────────────────────────────────────

export function initActividadesDelegate() {
    const lista = document.getElementById('actividades-lista');
    if (!lista) return;

    lista.addEventListener('click', async e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const { action, id, fecha } = btn.dataset;

        if (action === 'activar-evidencia')   await activarEvidencia(id);
        if (action === 'editar-fecha-fin')    await editarFechaFin(id, fecha ?? '');
        if (action === 'eliminar-actividad')  await eliminarActividad(id);

        // Las acciones de editar-actividad, crear-seccion, editar-seccion, etc.
        // las captura side-panel.js sobre el mismo elemento con su propio listener.
    });
}
