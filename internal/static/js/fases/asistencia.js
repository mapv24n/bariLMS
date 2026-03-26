// ── Panel de Asistencia ──

import { state } from './state.js';
import { escapar } from './utils.js';

// ─── Abrir panel ──────────────────────────────────────────────────────────────

export function clickAsistencia() {
    document.querySelectorAll('.act-proy-btn').forEach(b => b.classList.remove('active'));
    document.dispatchEvent(new CustomEvent('fases:set-mode', { detail: 'asistencia' }));
    state.asistenciaAprendices = [];
    document.getElementById('asistencia-content').style.display = 'none';
    document.getElementById('asistencia-fecha').value = new Date().toISOString().split('T')[0];
}

// ─── Carga y render ───────────────────────────────────────────────────────────

export async function cargarAsistencia() {
    const fecha = document.getElementById('asistencia-fecha').value;
    if (!fecha) { alert('Selecciona una fecha.'); return; }

    document.getElementById('asistencia-loading').style.display = 'block';
    document.getElementById('asistencia-content').style.display = 'none';

    const res  = await fetch(`/api/instructor/ficha/${window.FICHA_ID}/asistencia?fecha=${fecha}`);
    const data = await res.json();

    document.getElementById('asistencia-loading').style.display = 'none';
    state.asistenciaAprendices = data.aprendices || [];
    _renderAsistencia(state.asistenciaAprendices);
}

function _renderAsistencia(aprendices) {
    const container = document.getElementById('asistencia-tabla');
    if (!aprendices || aprendices.length === 0) {
        container.innerHTML = `
        <div class="empty-state py-3">
            <i class="fas fa-users fa-2x mb-2"></i>
            <p class="mb-0">No hay aprendices registrados en esta ficha.</p>
        </div>`;
        document.getElementById('asistencia-content').style.display = 'block';
        return;
    }

    let html = `<div class="table-responsive">
        <table class="table table-bordered mb-0" style="font-size:.85rem;">
            <thead class="thead-light">
                <tr>
                    <th>Documento</th>
                    <th>Aprendiz</th>
                    <th class="text-center text-success">Presente</th>
                    <th class="text-center text-danger">Ausente</th>
                    <th class="text-center text-warning">Excusa</th>
                </tr>
            </thead>
            <tbody>`;

    aprendices.forEach((ap, i) => {
        const p = ap.estado === 'Presente';
        const a = ap.estado === 'Ausente';
        const e = ap.estado === 'Excusa';
        html += `
        <tr>
            <td class="text-muted small align-middle">${escapar(ap.documento || '—')}</td>
            <td class="font-weight-bold align-middle">${escapar(ap.nombre)}</td>
            <td class="text-center align-middle">
                <input type="radio" name="asist-${i}" value="Presente"
                       data-action="asistencia-estado" data-idx="${i}" data-estado="Presente" ${p ? 'checked' : ''}>
            </td>
            <td class="text-center align-middle">
                <input type="radio" name="asist-${i}" value="Ausente"
                       data-action="asistencia-estado" data-idx="${i}" data-estado="Ausente"  ${a ? 'checked' : ''}>
            </td>
            <td class="text-center align-middle">
                <input type="radio" name="asist-${i}" value="Excusa"
                       data-action="asistencia-estado" data-idx="${i}" data-estado="Excusa"   ${e ? 'checked' : ''}>
            </td>
        </tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
    document.getElementById('asistencia-ok').style.display    = 'none';
    document.getElementById('asistencia-content').style.display = 'block';
}

function _actualizarEstadoAp(idx, estado) {
    if (state.asistenciaAprendices[idx]) {
        state.asistenciaAprendices[idx].estado = estado;
    }
}

export async function guardarAsistencia() {
    const fecha = document.getElementById('asistencia-fecha').value;
    if (!fecha) { alert('Sin fecha seleccionada.'); return; }

    const registros = state.asistenciaAprendices.map(ap => ({
        id_aprendiz: ap.id,
        estado:      ap.estado || 'Presente',
    }));

    const res  = await fetch(`/api/instructor/ficha/${window.FICHA_ID}/asistencia`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha, registros }),
    });
    const data = await res.json();
    if (data.ok) {
        document.getElementById('asistencia-ok').style.display = 'block';
    } else {
        alert('Error al guardar: ' + (data.error || 'Intenta de nuevo.'));
    }
}

// ─── Delegación de eventos ────────────────────────────────────────────────────

export function initAsistenciaDelegate() {
    document.getElementById('asistencia-tabla')?.addEventListener('change', e => {
        const input = e.target.closest('[data-action="asistencia-estado"]');
        if (!input) return;
        _actualizarEstadoAp(parseInt(input.dataset.idx), input.dataset.estado);
    });
}
