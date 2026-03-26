// ── Utilidades compartidas ──

import { sortableInstances } from './state.js';

/**
 * Muestra una alerta inline dentro de un formulario.
 * @param {string} alertId  - id del elemento <div class="alert">
 * @param {string} type     - 'success' | 'danger' | 'warning'
 * @param {string} message  - HTML del mensaje
 * @param {boolean} autohide - false para no ocultar automáticamente
 */
export function showFormAlert(alertId, type, message, autohide) {
    const el = document.getElementById(alertId);
    if (!el) return;
    el.className = `alert alert-${type}`;
    el.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} mr-1"></i>${message}`;
    el.style.display = 'block';
    if (autohide !== false && type === 'success') {
        setTimeout(() => { el.style.display = 'none'; }, 3500);
    }
}

/** Oculta una alerta inline. */
export function hideFormAlert(alertId) {
    const el = document.getElementById(alertId);
    if (el) el.style.display = 'none';
}

/** Escapa caracteres HTML para evitar XSS en strings interpolados. */
export function escapar(s) {
    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** Formatea una fecha ISO a "dd mmm yyyy". */
export function formatFecha(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
    return `${d.getUTCDate()} ${meses[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

/** Destruye una instancia de Sortable y la elimina del mapa. */
export function destroySortable(key) {
    if (sortableInstances.has(key)) {
        sortableInstances.get(key).destroy();
        sortableInstances.delete(key);
    }
}
