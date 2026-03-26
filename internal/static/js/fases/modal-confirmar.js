// ── Modal de confirmación reutilizable ──
//
// Reemplaza el confirm() nativo del navegador por un modal Bootstrap 4
// que respeta el estilo del proyecto BARÍ LMS.
//
// Uso:
//   import { confirmar } from './modal-confirmar.js';
//   const ok = await confirmar('¿Eliminar esta sección y todo su contenido?');
//   if (!ok) return;

/**
 * Muestra el modal de confirmación y devuelve una Promise<boolean>.
 * @param {string} mensaje  - Texto que ve el usuario.
 * @returns {Promise<boolean>} true si confirma, false si cancela.
 */
export function confirmar(mensaje) {
    return new Promise(resolve => {
        const modal  = document.getElementById('modalConfirmar');
        const btnOk  = document.getElementById('modal-confirmar-ok');
        const msgEl  = document.getElementById('modal-confirmar-mensaje');

        if (!modal || !btnOk || !msgEl) {
            // Fallback por si el modal no está incluido en el HTML
            resolve(window.confirm(mensaje));
            return;
        }

        msgEl.textContent = mensaje;

        // Mostrar modal via jQuery/Bootstrap 4
        $(modal).modal('show');

        function onOk() {
            $(modal).modal('hide');
            resolve(true);
            cleanup();
        }

        function onHide() {
            resolve(false);
            cleanup();
        }

        function cleanup() {
            btnOk.removeEventListener('click', onOk);
            $(modal).off('hidden.bs.modal', onHide);
        }

        btnOk.addEventListener('click', onOk, { once: true });
        $(modal).one('hidden.bs.modal', onHide);
    });
}
