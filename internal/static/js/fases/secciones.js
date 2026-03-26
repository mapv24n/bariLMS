// ── Render y Sortable de Secciones / Sub-secciones ──

import { state, sortableInstances } from './state.js';
import { escapar, formatFecha, destroySortable } from './utils.js';

// ─── Render ───────────────────────────────────────────────────────────────────

export function renderSecciones(secciones, actId) {
    if (!secciones || secciones.length === 0) return '';

    let html = `<div class="accordion" id="accordionSec${actId}">`;
    secciones.forEach(sec => {
        state._secData[sec.id] = sec;
        const colId   = `collapseSec${sec.id}`;
        const headId  = `headingSec${sec.id}`;
        const inicio  = sec.fecha_inicio ? formatFecha(sec.fecha_inicio) : '';
        const fin     = sec.fecha_fin    ? formatFecha(sec.fecha_fin)    : '';

        html += `
        <div class="card mb-1 shadow-sm seccion-card" data-id="${sec.id}" style="border:1px solid #e3e6f0;">
            <div class="card-header bg-white py-2 d-flex align-items-center" id="${headId}" style="gap:6px;">
                <i class="fas fa-grip-vertical sec-drag-handle text-muted"
                   title="Arrastrar para reordenar"
                   style="cursor:grab; font-size:.85em; flex-shrink:0; padding:4px 2px;"></i>
                <button class="btn btn-link text-left text-primary font-weight-bold text-decoration-none p-0 flex-grow-1 d-flex align-items-center"
                        type="button" data-toggle="collapse" data-target="#${colId}">
                    <i class="fas fa-layer-group mr-2" style="font-size:0.8rem;"></i> ${escapar(sec.nombre)}
                </button>
                <div style="flex-shrink:0;">
                    <button class="btn btn-sm btn-link text-secondary p-0 mx-1"
                            data-action="editar-seccion" data-id="${sec.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger p-0 mr-2"
                            data-action="eliminar-seccion" data-id="${sec.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success border-0 py-0" style="font-size:0.75rem;"
                            data-action="crear-subseccion" data-id="${sec.id}">
                        <i class="fas fa-plus"></i> Sub-sección
                    </button>
                </div>
            </div>
            <div id="${colId}" class="collapse" aria-labelledby="${headId}" data-parent="#accordionSec${actId}">
                <div class="card-body p-2" style="background:#fdfdfd;">
                    ${sec.descripcion ? `<div class="small text-muted mb-2 px-2">${escapar(sec.descripcion)}</div>` : ''}
                    <div class="px-2 mb-2 d-flex flex-wrap align-items-center" style="gap:6px; font-size:.75rem;">
                        ${sec.archivo_url ? `<a href="${sec.archivo_url}" target="_blank" class="badge badge-info border text-white"><i class="fas fa-link mr-1"></i>URL / Documento</a>` : ''}
                        ${inicio ? `<span class="badge badge-light border text-muted"><i class="fas fa-calendar mr-1"></i>Ini: ${inicio}</span>` : ''}
                        ${fin    ? `<span class="badge badge-light border text-muted"><i class="fas fa-calendar-times mr-1"></i>Fin: ${fin}</span>` : ''}
                    </div>
                    <hr class="mt-1 mb-2">
                    ${renderSubSecciones(sec.sub_secciones, sec.id)}
                </div>
            </div>
        </div>`;
    });
    html += '</div>';
    return html;
}

export function renderSubSecciones(subsecciones, secId) {
    if (!subsecciones || subsecciones.length === 0)
        return '<div class="text-muted small p-2">No hay sub-secciones en esta sección.</div>';

    let html = `<ul class="list-group list-group-flush border rounded" id="subsec-list-${secId}">`;
    subsecciones.forEach(sub => {
        state._subData[sub.id] = sub;
        const inicio = sub.fecha_inicio ? formatFecha(sub.fecha_inicio) : '';
        const fin    = sub.fecha_fin    ? formatFecha(sub.fecha_fin)    : '';
        html += `
        <li class="list-group-item p-2" data-id="${sub.id}">
            <div class="d-flex align-items-start" style="gap:6px;">
                <i class="fas fa-grip-vertical sub-drag-handle text-muted mt-1"
                   title="Arrastrar para reordenar"
                   style="cursor:grab; font-size:.85em; flex-shrink:0;"></i>
                <div style="flex:1; min-width:0;">
                    <div class="font-weight-bold" style="font-size:0.85rem; color:#4e73df;">${escapar(sub.nombre)}</div>
                    ${sub.descripcion ? `<div class="small text-muted mt-1">${escapar(sub.descripcion)}</div>` : ''}
                    <div class="mt-1 d-flex flex-wrap align-items-center" style="gap:6px; font-size:.75rem;">
                        ${sub.archivo_url ? `<a href="${sub.archivo_url}" target="_blank" class="badge badge-info border text-white"><i class="fas fa-link mr-1"></i>URL</a>` : ''}
                        ${inicio ? `<span class="badge badge-light border text-muted"><i class="fas fa-calendar mr-1"></i>Ini: ${inicio}</span>` : ''}
                        ${fin    ? `<span class="badge badge-light border text-muted"><i class="fas fa-calendar-times mr-1"></i>Fin: ${fin}</span>` : ''}
                    </div>
                </div>
                <div style="flex-shrink:0;">
                    <button class="btn btn-sm btn-link text-info p-0 mx-1"
                            data-action="editar-subseccion" data-id="${sub.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger p-0"
                            data-action="eliminar-subseccion" data-id="${sub.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </li>`;
    });
    html += '</ul>';
    return html;
}

// ─── Sortable ─────────────────────────────────────────────────────────────────

export function initSortableSecciones(actId) {
    const el = document.getElementById(`accordionSec${actId}`);
    if (!el) return;
    destroySortable(`sec-${actId}`);
    const s = new Sortable(el, {
        handle: '.sec-drag-handle',
        animation: 150,
        ghostClass: 'bg-light',
        onEnd: async () => {
            const orden = Array.from(el.querySelectorAll('.seccion-card[data-id]'))
                .map(c => parseInt(c.dataset.id));
            await fetch(`/api/instructor/actividad-aprendizaje/${actId}/secciones/orden`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ orden }),
            });
        },
    });
    sortableInstances.set(`sec-${actId}`, s);
}

export function initSortableSubSecciones(secId) {
    const el = document.getElementById(`subsec-list-${secId}`);
    if (!el) return;
    destroySortable(`sub-${secId}`);
    const s = new Sortable(el, {
        handle: '.sub-drag-handle',
        animation: 150,
        ghostClass: 'bg-light',
        onEnd: async () => {
            const orden = Array.from(el.querySelectorAll('li[data-id]'))
                .map(li => parseInt(li.dataset.id));
            await fetch(`/api/instructor/seccion/${secId}/sub-secciones/orden`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ orden }),
            });
        },
    });
    sortableInstances.set(`sub-${secId}`, s);
}
