// ── Estado global compartido entre módulos ──
// Todos los módulos importan este objeto y leen/escriben sobre él.
// Usar un objeto evita el problema de re-exportación de primitivos en ES modules.

export const state = {
    currentMode: null,           // 'actividad' | 'calificaciones' | 'asistencia'
    selectedActProyId: null,     // ID de la Actividad de Proyecto activa
    sidePanelMode: null,         // 'crear' | 'editar' | 'sec_crear' | 'sec_editar' | 'sub_crear' | 'sub_editar'
    matrizData: null,            // caché de la matriz de evidencias
    currentEntregaId: null,      // entrega abierta en panel calificaciones
    editingActId: null,          // actividad que se está editando/a la que se agrega sección
    actividadesCache: [],        // lista de actividades de aprendizaje cargadas
    currentSecId: null,          // sección activa en formulario
    currentSubId: null,          // sub-sección activa en formulario
    guiasCache: [],              // guías de la AP activa
    treeData: [],                // árbol completo (fases + APs) para poblar selectores
    calActProyId: null,          // AP seleccionada en el panel de calificaciones
    calTab: 1,                   // pestaña activa en calificaciones
    asistenciaAprendices: [],    // caché para guardar asistencia

    _apData: {},                 // { [apId]: { faseId, nombre, guias_count } }
    _secData: {},                // { [secId]: secObj }
    _subData: {},                // { [subId]: subObj }
};

/** Instancias de SortableJS activas, indexadas por clave. */
export const sortableInstances = new Map();
