/**
 * EPFormBuilder — constructor de formularios para Etapa Productiva.
 *
 * Recibe un array de secciones (producido por DatosSeguimientoEP) con la forma:
 *   [{ id, label, fields: [{ key, label, type, value, options? }] }]
 *
 * Tipos de campo soportados (explícitos — no se detectan):
 *   text | date | email | tel | number | textarea
 *   checkbox         → <input type="checkbox">
 *   checkbox-group   → lista de checkboxes, value es array de seleccionados
 *   select           → <select> con options
 *   eval-pair        → fila: select valoración + textarea observaciones
 *
 * Uso:
 *   EPFormBuilder.render('id-script-json', 'id-contenedor');
 */
const EPFormBuilder = (function () {

    // ── Utilidades ─────────────────────────────────────────────────────────

    function esc(str) {
        return String(str ?? '')
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function inputId(sectionId, key) {
        return `ep__${sectionId}__${key}`;
    }

    // ── Constructores por tipo ──────────────────────────────────────────────

    function buildText(f, sectionId) {
        const id = inputId(sectionId, f.key);
        return `
        <div class="col-md-6 form-group">
            <label for="${id}" class="small font-weight-bold text-gray-700">${esc(f.label)}</label>
            <input type="${f.type}" id="${id}" name="${id}"
                   class="form-control form-control-sm" value="${esc(f.value)}" autocomplete="off">
        </div>`;
    }

    function buildNumber(f, sectionId) {
        const id = inputId(sectionId, f.key);
        return `
        <div class="col-md-4 form-group">
            <label for="${id}" class="small font-weight-bold text-gray-700">${esc(f.label)}</label>
            <input type="number" id="${id}" name="${id}"
                   class="form-control form-control-sm" value="${esc(f.value)}">
        </div>`;
    }

    function buildTextarea(f, sectionId) {
        const id = inputId(sectionId, f.key);
        return `
        <div class="col-md-12 form-group">
            <label for="${id}" class="small font-weight-bold text-gray-700">${esc(f.label)}</label>
            <textarea id="${id}" name="${id}" rows="3"
                      class="form-control form-control-sm">${esc(f.value)}</textarea>
        </div>`;
    }

    function buildCheckbox(f, sectionId) {
        const id = inputId(sectionId, f.key);
        const checked = f.value ? ' checked' : '';
        return `
        <div class="col-md-12 form-group mb-1">
            <div class="form-check">
                <input type="checkbox" class="form-check-input" id="${id}" name="${id}"${checked}>
                <label class="form-check-label small" for="${id}">${esc(f.label)}</label>
            </div>
        </div>`;
    }

    function buildCheckboxGroup(f, sectionId) {
        const selected = Array.isArray(f.value) ? f.value : [];
        const boxes = (f.options || []).map(opt => {
            const id = inputId(sectionId, f.key + '__' + opt.toLowerCase().replace(/\s+/g, '_'));
            const checked = selected.includes(opt) ? ' checked' : '';
            return `
            <div class="form-check form-check-inline">
                <input type="checkbox" class="form-check-input" id="${id}" name="${inputId(sectionId, f.key)}[]"
                       value="${esc(opt)}"${checked}>
                <label class="form-check-label small" for="${id}">${esc(opt)}</label>
            </div>`;
        }).join('');

        return `
        <div class="col-md-12 form-group">
            <label class="small font-weight-bold text-gray-700 d-block">${esc(f.label)}</label>
            <div>${boxes}</div>
        </div>`;
    }

    function buildSelect(f, sectionId) {
        const id = inputId(sectionId, f.key);
        const opts = (f.options || []).map(opt => {
            const sel = opt === f.value ? ' selected' : '';
            return `<option value="${esc(opt)}"${sel}>${esc(opt)}</option>`;
        }).join('');

        return `
        <div class="col-md-6 form-group">
            <label for="${id}" class="small font-weight-bold text-gray-700">${esc(f.label)}</label>
            <select id="${id}" name="${id}" class="form-control form-control-sm">
                <option value="">— Seleccionar —</option>
                ${opts}
            </select>
        </div>`;
    }

    function buildEvalPair(f, sectionId) {
        const val = f.value || {};
        const idVal = inputId(sectionId, f.key + '__valoracion');
        const idObs = inputId(sectionId, f.key + '__observaciones');

        return `
        <div class="col-md-12 form-group">
            <label class="small font-weight-bold text-gray-700">${esc(f.label)}</label>
            <div class="row">
                <div class="col-md-3">
                    <label for="${idVal}" class="small text-muted">Valoración</label>
                    <input type="text" id="${idVal}" name="${idVal}"
                           class="form-control form-control-sm" value="${esc(val.valoracion || '')}">
                </div>
                <div class="col-md-9">
                    <label for="${idObs}" class="small text-muted">Observaciones</label>
                    <textarea id="${idObs}" name="${idObs}" rows="2"
                              class="form-control form-control-sm">${esc(val.observaciones || '')}</textarea>
                </div>
            </div>
        </div>`;
    }

    // ── Dispatcher ─────────────────────────────────────────────────────────

    function buildField(f, sectionId) {
        switch (f.type) {
            case 'text':
            case 'date':
            case 'email':
            case 'tel':      return buildText(f, sectionId);
            case 'number':   return buildNumber(f, sectionId);
            case 'textarea': return buildTextarea(f, sectionId);
            case 'checkbox': return buildCheckbox(f, sectionId);
            case 'checkbox-group': return buildCheckboxGroup(f, sectionId);
            case 'select':   return buildSelect(f, sectionId);
            case 'eval-pair': return buildEvalPair(f, sectionId);
            default:
                console.warn('EPFormBuilder: tipo de campo desconocido:', f.type, f.key);
                return buildText(f, sectionId);
        }
    }

    function buildSection(section) {
        const collapseId = `ep-section-${section.id}`;
        const fieldsHtml = section.fields.map(f => buildField(f, section.id)).join('');

        return `
        <div class="card shadow-sm mb-3">
            <div class="card-header py-2 bg-white border-bottom d-flex justify-content-between align-items-center"
                 style="cursor:pointer" data-toggle="collapse" data-target="#${collapseId}"
                 aria-expanded="true" aria-controls="${collapseId}">
                <span class="font-weight-bold text-sena small text-uppercase">${esc(section.label)}</span>
                <i class="fas fa-chevron-down fa-xs text-muted"></i>
            </div>
            <div id="${collapseId}" class="collapse show">
                <div class="card-body py-3">
                    <div class="form-row">${fieldsHtml}</div>
                </div>
            </div>
        </div>`;
    }

    // ── API pública ────────────────────────────────────────────────────────

    function render(scriptId, containerId) {
        const scriptEl   = document.getElementById(scriptId);
        const container  = document.getElementById(containerId);

        if (!scriptEl || !container) {
            console.warn('EPFormBuilder: elemento no encontrado —', scriptId, containerId);
            return;
        }

        let data;
        try {
            data = JSON.parse(scriptEl.textContent);
        } catch (e) {
            container.innerHTML =
                '<div class="alert alert-danger small">Error al cargar el formulario.</div>';
            console.error('EPFormBuilder: JSON inválido', e);
            return;
        }

        container.innerHTML = data.map(buildSection).join('');
    }

    return { render };
})();
