// ── Panel de Calificaciones ──

import { state } from './state.js';
import { escapar, showFormAlert, hideFormAlert } from './utils.js';

// ─── Abrir panel ──────────────────────────────────────────────────────────────

export function clickCalificaciones() {
    document.querySelectorAll('.act-proy-btn').forEach(b => b.classList.remove('active'));
    // setMode se llama desde tree.js; aquí solo preparamos el panel
    document.dispatchEvent(new CustomEvent('fases:set-mode', { detail: 'calificaciones' }));
    _poblarSelectorCalAP();
    document.getElementById('cal-tabs').style.display     = 'none';
    document.getElementById('cal-flex-row').style.display = 'none';
    state.matrizData    = null;
    state.calActProyId  = null;
}

function _poblarSelectorCalAP() {
    const sel = document.getElementById('cal-ap-selector');
    sel.innerHTML = '<option value="">-- Seleccionar --</option>';
    state.treeData.forEach(fase => {
        fase.actividades_proyecto.forEach(ap => {
            const opt = document.createElement('option');
            opt.value       = ap.id;
            opt.textContent = `${fase.nombre} › ${ap.nombre}`;
            sel.appendChild(opt);
        });
    });
}

// ─── Selección de AP en calificaciones ───────────────────────────────────────

export async function seleccionarCalAP() {
    const apId = document.getElementById('cal-ap-selector').value;
    if (!apId) {
        document.getElementById('cal-tabs').style.display     = 'none';
        document.getElementById('cal-flex-row').style.display = 'none';
        return;
    }
    state.calActProyId = apId;
    state.matrizData   = null;
    document.getElementById('cal-tabs').style.display = 'flex';
    document.getElementById('cal-flex-row').style.removeProperty('display');
    hideSidePanelCal();
    await setCalTab(1);
}

// ─── Pestañas ─────────────────────────────────────────────────────────────────

export async function setCalTab(tab) {
    state.calTab = tab;
    ['cal-tab-link-1', 'cal-tab-link-2'].forEach(id =>
        document.getElementById(id).classList.remove('active'));
    document.getElementById(`cal-tab-link-${tab}`).classList.add('active');
    document.getElementById('cal-tab-1-content').style.display = tab === 1 ? 'block' : 'none';
    document.getElementById('cal-tab-2-content').style.display = tab === 2 ? 'block' : 'none';

    if (!state.matrizData) {
        const res      = await fetch(`/api/instructor/actividad-proyecto/${state.calActProyId}/evidencias-matriz`);
        state.matrizData = await res.json();
    }
    if (tab === 1) _renderMatriz(state.matrizData);
    else           _renderCalificaciones(state.matrizData);
}

// ─── Render: Matriz de evidencias ─────────────────────────────────────────────

function _renderMatriz(data) {
    const container = document.getElementById('cal-tab-1-content');
    if (!data.actividades || data.actividades.length === 0) {
        container.innerHTML = `
        <div class="empty-state py-4">
            <i class="fas fa-clipboard fa-2x mb-2"></i>
            <p class="mb-0">No hay actividades de aprendizaje para mostrar evidencias.</p>
        </div>`;
        return;
    }

    let html = `<div class="table-responsive">
        <table class="table table-bordered table-hover mb-0" style="font-size:.82rem;">
            <thead class="thead-dark"><tr>
                <th style="white-space:nowrap;">Documento</th>
                <th>Aprendiz</th>`;
    data.actividades.forEach((act, i) => {
        html += `<th style="min-width:90px; text-align:center;">Actividad ${i + 1}<br>
            <small class="font-weight-normal" style="font-size:.72rem;">${escapar(act.nombre)}</small></th>`;
    });
    html += `</tr></thead><tbody>`;

    data.aprendices.forEach((ap, apIdx) => {
        html += `<tr>
            <td class="small text-muted align-middle">${escapar(ap.documento || '—')}</td>
            <td class="font-weight-bold align-middle">${escapar(ap.nombre)}</td>`;
        ap.entregas.forEach(e => {
            const cal      = e.entrega ? e.entrega.calificacion : null;
            const aprobado = cal !== null && cal !== undefined && parseFloat(cal) >= 75;
            const colorCal = cal !== null && cal !== undefined
                ? (aprobado ? 'style="color:#1cc88a;"' : 'style="color:#e74a3b;"') : '';
            html += `<td class="text-center align-middle">
                ${e.entrega
                    ? `<button class="btn btn-sm btn-link p-0" ${colorCal}
                               data-action="abrir-evidencia-cal"
                               data-ap-idx="${apIdx}"
                               data-actividad-id="${e.actividad_id}">
                           <i class="fas fa-eye mr-1"></i><span>${cal !== null && cal !== undefined ? cal : '—'}</span>
                       </button>`
                    : `<span class="text-muted">—</span>`
                }</td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

// ─── Render: Total de Calificaciones ─────────────────────────────────────────

function _renderCalificaciones(data) {
    const container = document.getElementById('cal-tab-2-content');
    if (!data.actividades || data.actividades.length === 0) {
        container.innerHTML = `
        <div class="empty-state py-4">
            <i class="fas fa-chart-bar fa-2x mb-2"></i>
            <p class="mb-0">No hay calificaciones para mostrar.</p>
        </div>`;
        return;
    }

    let html = `<div class="table-responsive">
        <table class="table table-bordered mb-0" style="font-size:.82rem;">
            <thead class="thead-dark"><tr><th>Aprendiz</th>`;
    data.actividades.forEach((act, i) => {
        html += `<th class="text-center" title="${escapar(act.nombre)}">Act. ${i + 1}</th>`;
    });
    html += `<th class="text-center">Total</th></tr></thead><tbody>`;

    data.aprendices.forEach(ap => {
        let suma = 0, celdas = '';
        ap.entregas.forEach(e => {
            const cal      = e.entrega ? e.entrega.calificacion : null;
            if (cal !== null && cal !== undefined) suma += parseFloat(cal);
            const aprobado = cal !== null && cal !== undefined && parseFloat(cal) >= 75;
            const cls      = cal !== null && cal !== undefined
                ? (aprobado ? 'class="text-success font-weight-bold"' : 'class="text-danger font-weight-bold"') : '';
            celdas += `<td class="text-center" ${cls}>${cal !== null && cal !== undefined ? cal : '—'}</td>`;
        });
        const n     = data.actividades.length;
        const total = n > 0 ? (suma / n).toFixed(1) : '—';
        const totalCls = n > 0 ? (parseFloat(total) >= 75 ? 'text-success font-weight-bold' : 'text-danger font-weight-bold') : 'text-muted';
        html += `<tr><td class="font-weight-bold">${escapar(ap.nombre)}</td>${celdas}
            <td class="text-center ${totalCls}">${total}</td></tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

// ─── Panel lateral de evidencia ───────────────────────────────────────────────

function _abrirEvidenciaCal(apIdx, actividadId) {
    if (!state.matrizData) return;
    const ap   = state.matrizData.aprendices[apIdx];
    const act  = state.matrizData.actividades.find(a => a.id === actividadId);
    const eObj = ap.entregas.find(e => e.actividad_id === actividadId);
    if (!eObj || !eObj.entrega) return;

    state.currentEntregaId = eObj.entrega.id;
    document.getElementById('ev-aprendiz').textContent   = ap.nombre;
    document.getElementById('ev-actividad').textContent  = act ? act.nombre : '';
    document.getElementById('ev-url').value              = eObj.entrega.url || '';
    document.getElementById('ev-url-link').href          = eObj.entrega.url || '#';
    document.getElementById('ev-observaciones').value    = '';
    const cal = eObj.entrega.calificacion;
    document.getElementById('ev-calificacion').value     = cal !== null && cal !== undefined ? cal : '';
    _actualizarBadge(cal);
    document.getElementById('side-panel-cal').style.display = 'block';
}

export function hideSidePanelCal() {
    state.currentEntregaId = null;
    document.getElementById('side-panel-cal').style.display = 'none';
}

function _actualizarBadge(cal) {
    const el = document.getElementById('ev-estado-badge');
    if (cal === null || cal === undefined || cal === '') { el.innerHTML = ''; return; }
    const c = parseFloat(cal);
    el.innerHTML = c >= 75
        ? `<span class="badge badge-aprobado px-2 py-1"><i class="fas fa-check mr-1"></i>APROBADO (${c})</span>`
        : `<span class="badge badge-reprobado px-2 py-1"><i class="fas fa-times mr-1"></i>REPROBADO (${c})</span>`;
}

export async function guardarCalificacion() {
    if (!state.currentEntregaId) {
        showFormAlert('form-evidencia-alert', 'danger', 'No hay entrega seleccionada.', false);
        return;
    }
    const calVal = document.getElementById('ev-calificacion').value;
    if (calVal === '') { showFormAlert('form-evidencia-alert', 'danger', 'Ingresa una calificación.', false); return; }
    const cal = parseFloat(calVal);
    if (isNaN(cal) || cal < 0 || cal > 100) {
        showFormAlert('form-evidencia-alert', 'danger', 'La calificación debe estar entre 0 y 100.', false);
        return;
    }
    hideFormAlert('form-evidencia-alert');

    try {
        const res  = await fetch(`/api/instructor/entrega/${state.currentEntregaId}/calificar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ calificacion: cal, observaciones: document.getElementById('ev-observaciones').value.trim() }),
        });
        const data = await res.json();
        if (data.ok) {
            showFormAlert('form-evidencia-alert', 'success', 'Calificación guardada correctamente.');
            setTimeout(() => { hideSidePanelCal(); state.matrizData = null; setCalTab(state.calTab); }, 1200);
        } else {
            showFormAlert('form-evidencia-alert', 'danger', 'Error al guardar: ' + (data.error || 'Intenta de nuevo.'), false);
        }
    } catch {
        showFormAlert('form-evidencia-alert', 'danger', 'Error de conexión. Intenta de nuevo.', false);
    }
}

// ─── Delegación y listeners estáticos ────────────────────────────────────────

export function initCalificacionesDelegate() {
    // Listener en la tabla de evidencias (dinámica)
    document.getElementById('cal-tab-1-content')?.addEventListener('click', e => {
        const btn = e.target.closest('[data-action="abrir-evidencia-cal"]');
        if (!btn) return;
        _abrirEvidenciaCal(parseInt(btn.dataset.apIdx), btn.dataset.actividadId);
    });

    // Input calificación → actualiza badge en tiempo real
    document.getElementById('ev-calificacion')?.addEventListener('input', function () {
        _actualizarBadge(this.value);
    });
}
