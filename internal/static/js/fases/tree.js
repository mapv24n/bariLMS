// ── Árbol de Fases y navegación de paneles ──

import { state } from './state.js';
import { escapar } from './utils.js';
import { cargarGuias } from './guias.js';
import { cargarGuiasAprendizaje } from './guias-aprendizaje.js';
import { cargarActividades } from './actividades.js';
import { hideSidePanel } from './side-panel.js';

// ─── Cambio de modo (panel activo) ────────────────────────────────────────────

export function setMode(mode) {
    state.currentMode = mode;
    document.getElementById('panel-vacio').style.display          = 'none';
    document.getElementById('panel-actividad').style.display      = 'none';
    document.getElementById('panel-calificaciones').style.display = 'none';
    document.getElementById('panel-asistencia').style.display     = 'none';

    const modos = {
        actividad:       'panel-actividad',
        calificaciones:  'panel-calificaciones',
        asistencia:      'panel-asistencia',
    };
    const panelId = modos[mode] || 'panel-vacio';
    document.getElementById(panelId).style.display = 'block';
}

// ─── Carga y render del árbol ─────────────────────────────────────────────────

export async function cargarArbol() {
    const res  = await fetch(`/api/instructor/ficha/${window.FICHA_ID}/tree`);
    const data = await res.json();
    state.treeData = data.fases || [];
    renderArbol(state.treeData);
}

export function renderArbol(fases) {
    const container = document.getElementById('fase-tree');
    if (!fases || fases.length === 0) {
        container.innerHTML = `
        <div class="empty-state small p-2">
            <i class="fas fa-info-circle mb-1"></i>
            <p class="mb-0">Sin fases asignadas para esta ficha.</p>
        </div>`;
        return;
    }

    let html = '';
    fases.forEach(fase => {
        const colId = `fase-${fase.id}`;
        html += `
        <div class="mb-1">
            <button class="fase-btn collapsed" data-toggle="collapse" data-target="#${colId}">
                <span>
                    <i class="fas fa-layer-group mr-1" style="font-size:.8em;opacity:.85"></i>
                    ${escapar(fase.nombre)}
                </span>
                <i class="fas fa-chevron-down chevron" style="font-size:.75em;"></i>
            </button>
            <div class="collapse tree-indent-1" id="${colId}">`;

        if (fase.actividades_proyecto.length === 0) {
            html += `<p class="text-muted small px-2 py-1 mb-1">Sin actividades de proyecto.</p>`;
        }

        fase.actividades_proyecto.forEach(ap => {
            state._apData[ap.id] = { faseId: fase.id, nombre: ap.nombre, guias_count: ap.guias_count };
            const lockIcon = ap.guias_count === 0
                ? `<i class="fas fa-lock ml-1 text-warning" style="font-size:.7em;" title="Sin guías"></i>`
                : '';
            html += `
            <button class="act-proy-btn" id="btn-ap-${ap.id}" data-ap-id="${ap.id}">
                <span>
                    <i class="fas fa-folder mr-1" style="font-size:.8em;opacity:.8"></i>
                    ${escapar(ap.nombre)}${lockIcon}
                </span>
            </button>`;
        });

        html += `</div></div>`;
    });

    container.innerHTML = html;

    // Delegación: clic en una Actividad de Proyecto del árbol
    container.addEventListener('click', e => {
        const btn = e.target.closest('[data-ap-id]');
        if (!btn) return;
        const d = state._apData[btn.dataset.apId];
        if (d) seleccionarActProy(d.faseId, btn.dataset.apId, d.nombre, d.guias_count);
    });
}

// ─── Selección de Actividad de Proyecto ──────────────────────────────────────

export async function seleccionarActProy(faseId, apId, apNombre, guiasCount) {
    state.selectedActProyId = apId;
    state.matrizData        = null;

    document.querySelectorAll('.act-proy-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`btn-ap-${apId}`)?.classList.add('active');

    setMode('actividad');
    hideSidePanel();

    document.getElementById('ap-titulo-nombre').textContent = apNombre;

    await cargarGuias(apId);
    await cargarGuiasAprendizaje(apId);
    // La visibilidad de actividades-section se evalúa automáticamente 
    // mediante los eventos 'fases:evaluar-desbloqueo' lanzados por cargarGuias.
}

export async function evaluarDesbloqueoActividades() {
    const tieneConcertado = state.guiasCache && state.guiasCache.length > 0;
    const tieneAprendizaje = state.guiasAprendizajeCache && state.guiasAprendizajeCache.length > 0;
    
    const lock1 = document.getElementById('guias-lock');
    if (lock1) lock1.style.display = tieneConcertado ? 'none' : 'block';
    
    const lock2 = document.getElementById('guias-aprendizaje-lock');
    if (lock2) lock2.style.display = tieneAprendizaje ? 'none' : 'block';

    const actSection = document.getElementById('actividades-section');
    if (!actSection) return;

    if (tieneConcertado && tieneAprendizaje) {
        const estabaOculto = actSection.style.display === 'none' || actSection.style.display === '';
        actSection.style.display = 'block';
        if (estabaOculto && state.selectedActProyId) {
            await cargarActividades();
        }
    } else {
        actSection.style.display = 'none';
    }
}

document.addEventListener('fases:evaluar-desbloqueo', evaluarDesbloqueoActividades);
