/**
 * EPFormBuilder — constructor dinámico de formularios para Etapa Productiva.
 *
 * Lee un objeto JSON y construye inputs Bootstrap 4 según el tipo de dato:
 *   string   → <input type="text|date|email|tel">  (detectado por nombre de campo)
 *   boolean  → <input type="checkbox">
 *   number   → <input type="number">
 *   null     → <input type="text">  (valor aún no registrado)
 *   object (todos bool) → grupo de checkboxes (opciones múltiples)
 *   object (tiene "valorac*") → fila eval: select valoración + textarea observaciones
 *   object (anidado general) → sub-sección colapsable
 *
 * Uso:
 *   EPFormBuilder.render('id-del-script-json', 'id-del-contenedor');
 */
const EPFormBuilder = (function () {

    // ── Helpers ────────────────────────────────────────────────────────────

    function slug(str) {
        return str
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-|-$/g, '');
    }

    function fieldId(sectionKey, fieldKey) {
        return 'ep-' + slug(sectionKey) + '--' + slug(fieldKey);
    }

    /**
     * Detecta el type de <input> apropiado para un campo de texto
     * basándose en el nombre del campo.
     */
    function detectTextType(key) {
        const k = key.toLowerCase();
        if (k.includes('fecha') || k.includes('date')) return 'date';
        if (k.includes('correo') || k.includes('email')) return 'email';
        if (
            k.includes('telefono') || k.includes('teléfono') ||
            k.includes('contacto') || k.includes('fijo') || k.includes('móvil')
        ) return 'tel';
        return 'text';
    }

    /**
     * Clasifica el tipo lógico de un campo a partir de su valor y nombre.
     * Retorna: 'text' | 'checkbox' | 'number' | 'checkbox-group' | 'eval-pair' | 'sub-section'
     */
    function classifyField(key, value) {
        if (typeof value === 'boolean') return 'checkbox';
        if (typeof value === 'number') return 'number';
        if (value === null || typeof value === 'string') return 'text';

        if (typeof value === 'object') {
            const vals = Object.values(value);
            if (vals.length > 0 && vals.every(v => typeof v === 'boolean')) {
                return 'checkbox-group';
            }
            const keys = Object.keys(value).map(k => k.toLowerCase());
            if (keys.some(k => k.includes('valorac'))) {
                return 'eval-pair';
            }
            return 'sub-section';
        }
        return 'text';
    }

    // ── Constructores de elementos ─────────────────────────────────────────

    function buildTextInput(id, key, value) {
        const inputType = detectTextType(key);
        const div = document.createElement('div');
        div.className = 'col-md-6 form-group';
        div.innerHTML =
            `<label for="${id}" class="small font-weight-bold text-gray-700">${key}</label>` +
            `<input type="${inputType}" id="${id}" name="${id}"` +
            ` class="form-control form-control-sm"` +
            ` value="${_esc(value || '')}" autocomplete="off">`;
        return div;
    }

    function buildNumberInput(id, key, value) {
        const div = document.createElement('div');
        div.className = 'col-md-4 form-group';
        div.innerHTML =
            `<label for="${id}" class="small font-weight-bold text-gray-700">${key}</label>` +
            `<input type="number" id="${id}" name="${id}"` +
            ` class="form-control form-control-sm" value="${value !== null ? value : ''}">`;
        return div;
    }

    function buildCheckbox(id, key, value) {
        const div = document.createElement('div');
        div.className = 'col-md-12 form-group mb-1';
        div.innerHTML =
            `<div class="form-check">` +
            `<input type="checkbox" class="form-check-input" id="${id}" name="${id}"` +
            (value ? ' checked' : '') + `>` +
            `<label class="form-check-label small" for="${id}">${key}</label>` +
            `</div>`;
        return div;
    }

    function buildCheckboxGroup(sectionKey, key, options) {
        const div = document.createElement('div');
        div.className = 'col-md-12 form-group';

        let html = `<label class="small font-weight-bold text-gray-700 d-block">${key}</label>`;
        html += `<div class="d-flex flex-wrap">`;

        Object.entries(options).forEach(([optLabel, checked]) => {
            const oid = fieldId(sectionKey + '-' + key, optLabel);
            html +=
                `<div class="form-check mr-4">` +
                `<input type="checkbox" class="form-check-input" id="${oid}" name="${oid}"` +
                (checked ? ' checked' : '') + `>` +
                `<label class="form-check-label small" for="${oid}">${optLabel}</label>` +
                `</div>`;
        });

        html += `</div>`;
        div.innerHTML = html;
        return div;
    }

    function buildEvalPair(sectionKey, parentKey, pairObj) {
        const div = document.createElement('div');
        div.className = 'col-md-12 form-group';

        const baseId = fieldId(sectionKey, parentKey);

        let html = `<label class="small font-weight-bold text-gray-700 d-block">${parentKey}</label>`;
        html += `<div class="row">`;

        Object.entries(pairObj).forEach(([subKey, subVal]) => {
            const sid = baseId + '--' + slug(subKey);
            const isObs = subKey.toLowerCase().includes('observac');
            if (isObs) {
                html +=
                    `<div class="col-md-8">` +
                    `<label class="small text-muted" for="${sid}">${subKey}</label>` +
                    `<textarea id="${sid}" name="${sid}" rows="2"` +
                    ` class="form-control form-control-sm">${_esc(subVal || '')}</textarea>` +
                    `</div>`;
            } else {
                html +=
                    `<div class="col-md-4">` +
                    `<label class="small text-muted" for="${sid}">${subKey}</label>` +
                    `<input type="text" id="${sid}" name="${sid}"` +
                    ` class="form-control form-control-sm" value="${_esc(subVal || '')}">` +
                    `</div>`;
            }
        });

        html += `</div>`;
        div.innerHTML = html;
        return div;
    }

    function buildSubSection(sectionKey, parentKey, obj) {
        const div = document.createElement('div');
        div.className = 'col-md-12 mb-3';

        const collapseId = 'collapse-' + fieldId(sectionKey, parentKey);
        div.innerHTML =
            `<div class="border rounded">` +
            `<div class="px-3 py-2 bg-light d-flex justify-content-between align-items-center" ` +
            `style="cursor:pointer" data-toggle="collapse" data-target="#${collapseId}" ` +
            `aria-expanded="true" aria-controls="${collapseId}">` +
            `<span class="small font-weight-bold text-gray-700">${parentKey}</span>` +
            `<i class="fas fa-chevron-down fa-xs text-muted"></i>` +
            `</div>` +
            `<div id="${collapseId}" class="collapse show">` +
            `<div class="p-3"><div class="form-row" id="sub-${collapseId}"></div></div>` +
            `</div>` +
            `</div>`;

        const inner = div.querySelector('#sub-' + collapseId);
        const subSectionKey = sectionKey + '/' + parentKey;
        Object.entries(obj).forEach(([k, v]) => {
            inner.appendChild(buildField(subSectionKey, k, v));
        });

        return div;
    }

    function buildField(sectionKey, key, value) {
        const type = classifyField(key, value);
        const id = fieldId(sectionKey, key);

        switch (type) {
            case 'checkbox':
                return buildCheckbox(id, key, value);
            case 'number':
                return buildNumberInput(id, key, value);
            case 'checkbox-group':
                return buildCheckboxGroup(sectionKey, key, value);
            case 'eval-pair':
                return buildEvalPair(sectionKey, key, value);
            case 'sub-section':
                return buildSubSection(sectionKey, key, value);
            default:
                return buildTextInput(id, key, value);
        }
    }

    function buildSection(sectionName, fields) {
        const card = document.createElement('div');
        card.className = 'card shadow-sm mb-3';

        const sectionId = 'ep-section-' + slug(sectionName);
        card.innerHTML =
            `<div class="card-header py-2 bg-white border-bottom"` +
            ` style="cursor:pointer" data-toggle="collapse" data-target="#${sectionId}"` +
            ` aria-expanded="true">` +
            `<span class="font-weight-bold text-sena small text-uppercase">${sectionName}</span>` +
            `</div>` +
            `<div id="${sectionId}" class="collapse show">` +
            `<div class="card-body py-3">` +
            `<div class="form-row" id="fields-${sectionId}"></div>` +
            `</div></div>`;

        const container = card.querySelector('#fields-' + sectionId);
        Object.entries(fields).forEach(([k, v]) => {
            container.appendChild(buildField(sectionName, k, v));
        });

        return card;
    }

    // ── Escape helper ──────────────────────────────────────────────────────

    function _esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    // ── API pública ────────────────────────────────────────────────────────

    function render(scriptId, containerId) {
        const scriptEl = document.getElementById(scriptId);
        const container = document.getElementById(containerId);

        if (!scriptEl || !container) {
            console.warn('EPFormBuilder: elemento no encontrado', scriptId, containerId);
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

        container.innerHTML = '';
        Object.entries(data).forEach(([sectionName, fields]) => {
            container.appendChild(buildSection(sectionName, fields));
        });
    }

    return { render };
})();
