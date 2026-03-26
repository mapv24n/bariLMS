/**
 * instructor-fases.js — Punto de entrada (ES Module)
 *
 * Importa todos los submódulos, adjunta los event listeners a los elementos
 * estáticos del HTML y arranca la aplicación al cargar el DOM.
 *
 * FICHA_ID se define en fases.html antes de cargar este módulo.
 */

import { cargarArbol, setMode }                                from './fases/tree.js';
import { cargarActividades, initActividadesDelegate }          from './fases/actividades.js';
import { toggleFormGuia, subirGuia, initGuiasDelegate }        from './fases/guias.js';
import { toggleFormGuiaAprendizaje, subirGuiaAprendizaje, initGuiasDelegate as initGuiasAprendizajeDelegate } from './fases/guias-aprendizaje.js';
import { toggleCrearPanel, confirmarCrearActividad,
         guardarSeccion, guardarSubSeccion,
         hideSidePanel, initSidePanelDelegate }                from './fases/side-panel.js';
import { clickCalificaciones, seleccionarCalAP, setCalTab,
         guardarCalificacion, hideSidePanelCal,
         initCalificacionesDelegate }                          from './fases/calificaciones.js';
import { clickAsistencia, cargarAsistencia,
         guardarAsistencia, initAsistenciaDelegate }           from './fases/asistencia.js';

// ─── Inicialización ───────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {

    // ── Listeners estáticos del HTML ──────────────────────────────────────────

    // Árbol: botones de la barra lateral fija
    document.querySelector('[data-btn="calificaciones"]')
        ?.addEventListener('click', clickCalificaciones);
    document.querySelector('[data-btn="asistencia"]')
        ?.addEventListener('click', clickAsistencia);

    // Guías
    document.querySelector('[data-btn="toggle-form-guia"]')
        ?.addEventListener('click', toggleFormGuia);
    document.querySelector('[data-btn="subir-guia"]')
        ?.addEventListener('click', subirGuia);

    // Guías de Aprendizaje
    document.querySelector('[data-btn="toggle-form-guia-aprendizaje"]')
        ?.addEventListener('click', toggleFormGuiaAprendizaje);
    document.querySelector('[data-btn="subir-guia-aprendizaje"]')
        ?.addEventListener('click', subirGuiaAprendizaje);

    // Actividades
    document.querySelector('[data-btn="crear-actividad"]')
        ?.addEventListener('click', toggleCrearPanel);
    document.querySelector('[data-btn="confirmar-actividad"]')
        ?.addEventListener('click', confirmarCrearActividad);

    // Secciones / Sub-secciones (botones del side-panel)
    document.querySelector('[data-btn="guardar-seccion"]')
        ?.addEventListener('click', guardarSeccion);
    document.querySelector('[data-btn="guardar-subseccion"]')
        ?.addEventListener('click', guardarSubSeccion);

    // Calificaciones
    document.getElementById('cal-ap-selector')
        ?.addEventListener('change', seleccionarCalAP);
    document.getElementById('cal-tab-link-1')
        ?.addEventListener('click', e => { e.preventDefault(); setCalTab(1); });
    document.getElementById('cal-tab-link-2')
        ?.addEventListener('click', e => { e.preventDefault(); setCalTab(2); });
    document.querySelector('[data-btn="guardar-calificacion"]')
        ?.addEventListener('click', guardarCalificacion);

    // Asistencia
    document.querySelector('[data-btn="cargar-asistencia"]')
        ?.addEventListener('click', cargarAsistencia);
    document.querySelector('[data-btn="guardar-asistencia"]')
        ?.addEventListener('click', guardarAsistencia);

    // Cerrar paneles (botones ✕ y Cancelar de los formularios incluidos)
    document.addEventListener('click', e => {
        if (e.target.closest('[data-btn="cancelar-panel"]'))     hideSidePanel();
        if (e.target.closest('[data-btn="cancelar-panel-cal"]')) hideSidePanelCal();
    });

    // ── Delegaciones de eventos sobre contenedores dinámicos ─────────────────
    initGuiasDelegate();
    initGuiasAprendizajeDelegate();
    initActividadesDelegate();
    initSidePanelDelegate();
    initCalificacionesDelegate();
    initAsistenciaDelegate();

    // ── Eventos personalizados entre módulos ──────────────────────────────────

    // Refresco del árbol (después de subir/eliminar guía)
    document.addEventListener('fases:tree-refresh', cargarArbol);

    // Refresco de actividades (después de crear/editar/eliminar)
    document.addEventListener('fases:actividades-refresh', cargarActividades);

    // Cambio de modo solicitado por calificaciones/asistencia
    document.addEventListener('fases:set-mode', e => setMode(e.detail));

    // ── Arranque ──────────────────────────────────────────────────────────────
    cargarArbol();
});
