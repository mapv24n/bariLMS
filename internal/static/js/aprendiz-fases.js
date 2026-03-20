let fasesData = [];
let selectedCompId = null;
let selectedEvidenciaId = null;
let currentEntregaId = null;
let tieneEvidencia = false;
let submitting = false;

async function cargarArbol() {
    const res = await fetch(`/api/aprendiz/ficha/${FICHA_ID}/tree`);
    const data = await res.json();
    fasesData = data.fases || [];
    renderFases(fasesData);
}

function renderFases(fases) {
    const container = document.getElementById('fase-tree');
    if (fases.length === 0) {
        container.innerHTML = `<div class="empty-state"><p class="small mb-0">No hay fases.</p></div>`;
        return;
    }
    let html = '';
    fases.forEach((fase, fi) => {
        const faseTarget = `fase-${fase.id}`;
        html += `
        <div class="mb-1">
            <button class="fase-btn collapsed" data-toggle="collapse" data-target="#${faseTarget}">
                <span>${fase.nombre}</span>
            </button>
            <div class="collapse" id="${faseTarget}">`;

        fase.actividades_proyecto.forEach(ap => {
            html += `<button class="act-proy-btn" id="btn-ap-${ap.id}" onclick="seleccionarActProy(${fase.id}, ${ap.id})"><span>${ap.nombre}</span></button>`;
        });

        html += `</div></div>`;
    });
    container.innerHTML = html;
}

function seleccionarActProy(faseId, apId) {
    document.querySelectorAll('.act-proy-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`btn-ap-${apId}`).classList.add('active');

    document.getElementById('panel-vacio-center').classList.add('d-none');
    const container = document.getElementById('actividades-list-container');
    container.classList.remove('d-none');

    document.getElementById('panel-vacio-right').classList.remove('d-none');
    document.getElementById('panel-competencia-right').classList.add('d-none');
    document.getElementById('lbl-estado').className = 'estado-badge estado-pendiente';
    document.getElementById('lbl-estado').innerHTML = '<i class="fas fa-clock"></i> Pendiente';

    let apEncontrada = null;
    let faseNombre = '';
    for (const f of fasesData) {
        if (f.id === faseId) {
            faseNombre = f.nombre;
            apEncontrada = f.actividades_proyecto.find(a => a.id === apId);
            break;
        }
    }

    if (!apEncontrada || apEncontrada.competencias.length === 0) {
        container.innerHTML = `<div class="empty-state"><p>Sin actividades de aprendizaje configuradas.</p></div>`;
        return;
    }

    let html = '';
    apEncontrada.competencias.forEach((comp, idx) => {
        let estadoIcon = '<i class="fas fa-clock text-warning"></i>';
        if (comp.calificacion !== null) estadoIcon = (comp.calificacion >= 75) ? '<i class="fas fa-check-circle text-success"></i>' : '<i class="fas fa-times-circle text-danger"></i>';

        html += `
        <div class="comp-card bg-white p-3 mb-2" id="card-comp-${comp.id}" onclick="abrirCompetencia(${comp.id}, '${escapar(comp.nombre)}', ${comp.evidencia_id ? comp.evidencia_id : 'null'}, ${comp.evidencia_id ? `'${escapar(comp.evidencia_desc || '')}'` : 'null'}, ${comp.entrega_id ? comp.entrega_id : 'null'}, ${comp.entrega_id ? `'${escapar(comp.entrega_url || '')}'` : 'null'}, ${comp.entrega_id ? `'${escapar(comp.calificacion !== null ? comp.calificacion : '')}'` : 'null'}, ${comp.entrega_id ? `'${escapar(comp.observaciones || '')}'` : 'null'}, ${comp.evidencia_id ? 'true' : 'false'}, '${escapar(comp.guia_url || '')}')">
            <div class="d-flex justify-content-between align-items-center">
                <div class="text-gray-800 font-weight-bold" style="font-size:0.9rem;">${comp.nombre}</div>
                <div>${estadoIcon}</div>
            </div>
            <div class="mt-2 text-muted small"><i class="fas  mr-1"></i> Haz clic para ver detalles y entregar</div>
        </div>`;
    });
    container.innerHTML = html;
}

function abrirCompetencia(compId, nombre, evId, evDesc, entId, entUrl, calif, obs, tieneEv, guiaUrl) {
    selectedCompId = compId;
    selectedEvidenciaId = evId;
    currentEntregaId = entId;
    tieneEvidencia = tieneEv === true || tieneEv === 'true';

    document.querySelectorAll('.comp-card').forEach(c => c.classList.remove('active'));
    document.getElementById(`card-comp-${compId}`).classList.add('active');

    document.getElementById('panel-vacio-right').classList.add('d-none');
    document.getElementById('panel-competencia-right').classList.remove('d-none');

    document.getElementById('lbl-competencia').textContent = nombre;

    if (guiaUrl && guiaUrl !== 'null' && guiaUrl !== '') {
        document.getElementById('guia-container').innerHTML = `<a href="${guiaUrl}" target="_blank" class="guia-link"><i class="fas fa-external-link-alt"></i> Abrir Guía</a>`;
    } else {
        document.getElementById('guia-container').innerHTML = `<div class="sin-datos text-muted">No adjunta.</div>`;
    }

    if (evDesc && evDesc !== 'null' && evDesc !== '') {
        document.getElementById('evidencia-container').innerHTML = evDesc;
    } else {
        document.getElementById('evidencia-container').innerHTML = `<span class="text-muted">Aún no configurada por el instructor.</span>`;
    }

    renderEstadoEntrega(entId, entUrl, calif, obs);
}

function renderEstadoEntrega(entregaId, entregaUrl, calificacion, observaciones) {
    const estadoEl = document.getElementById('lbl-estado');
    const entregaEl = document.getElementById('entrega-container');
    const calEl = document.getElementById('calificacion-container');

    const hasEntrega = entregaId !== null && entregaId !== 'null';
    const urlVal = (entregaUrl && entregaUrl !== 'null') ? entregaUrl : '';
    const calVal = (calificacion && calificacion !== 'null' && calificacion !== '') ? parseFloat(calificacion) : null;
    const obsVal = (observaciones && observaciones !== 'null') ? observaciones : '';

    if (!tieneEvidencia) {
        estadoEl.className = 'estado-badge estado-pendiente';
        estadoEl.innerHTML = '<i class="fas fa-clock"></i> Sin evidencia';
        entregaEl.innerHTML = `<div class="sin-datos">No puedes entregar.</div>`;
        calEl.innerHTML = '';
        return;
    }

    if (hasEntrega && calVal !== null) {
        const esAprobado = calVal >= 75;
        estadoEl.className = `estado-badge ${esAprobado ? 'estado-aprobado' : 'estado-reprobado'}`;
        estadoEl.innerHTML = esAprobado ? '<i class="fas fa-check-circle"></i> Calificado' : '<i class="fas fa-times-circle"></i> Calificado';
        entregaEl.innerHTML = urlVal ? `<a href="${urlVal}" target="_blank" class="btn btn-sm btn-outline-success btn-block"><i class="fas fa-eye mr-1"></i>Ver entrega actual</a>` : 'Sin enlace';
        calEl.innerHTML = `
            <div class="calificacion-box mt-3">
                <div class="nota-grande ${esAprobado ? 'aprobado' : 'reprobado'}">${calVal} / 100</div>
                <div class="small text-muted mt-1">Calificación</div>
                ${obsVal ? `<div class="small mt-2 p-2 bg-white rounded text-left border"><strong>Obs:</strong> ${obsVal}</div>` : ''}
            </div>`;
    } else if (hasEntrega && urlVal) {
        estadoEl.className = 'estado-badge estado-entregado';
        estadoEl.innerHTML = '<i class="fas fa-clock"></i> Entregado';
        entregaEl.innerHTML = `
            <input type="url" class="form-control mb-2" id="input-url" value="${urlVal}" placeholder="Link...">
            <button class="btn btn-success btn-block" id="btn-entregar" onclick="entregarEvidencia()"><i class="fas fa-sync-alt mr-1"></i> Actualizar enlace</button>
            <a href="${urlVal}" target="_blank" class="d-block text-center mt-2 small text-sena">Ver enlace entregado</a>`;
        calEl.innerHTML = '';
    } else {
        estadoEl.className = 'estado-badge estado-pendiente';
        estadoEl.innerHTML = '<i class="fas fa-clock"></i> Sin entregar';
        entregaEl.innerHTML = `
            <input type="url" class="form-control mb-2" id="input-url" placeholder="https://drive.google.com/...">
            <button class="btn btn-success btn-block" id="btn-entregar" onclick="entregarEvidencia()"><i class="fas fa-paper-plane mr-1"></i> Enviar</button>`;
        calEl.innerHTML = '';
    }
}

async function entregarEvidencia() {
    if (submitting) return;
    const url = document.getElementById('input-url').value.trim();
    if (!url) { alert('Ingresa un enlace.'); return; }
    if (!selectedEvidenciaId) return;

    submitting = true;
    const btn = document.getElementById('btn-entregar');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Enviando...';

    const res = await fetch('/api/aprendiz/entrega', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ evidencia_id: selectedEvidenciaId, url: url, entrega_id: currentEntregaId })
    });
    const data = await res.json();
    if (data.ok) {
        currentEntregaId = data.entrega_id;
        for (const f of fasesData) {
            for (const ap of f.actividades_proyecto) {
                let comp = ap.competencias.find(c => c.id === selectedCompId);
                if (comp) {
                    comp.entrega_id = currentEntregaId;
                    comp.entrega_url = url;
                }
            }
        }
        alert('Evidencia registrada!');
        renderEstadoEntrega(currentEntregaId, url, null, null);
    } else {
        alert('Error: ' + data.error);
    }
    submitting = false;
    btn.disabled = false;
}

function escapar(s) { return (s || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"'); }

cargarArbol();
