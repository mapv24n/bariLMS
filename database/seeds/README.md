# Seeds de desarrollo — bariLMS

Datos de prueba para desarrollo y QA. Crean una cadena completa de datos realistas
con la que se pueden probar todos los módulos sin configuración manual.

## Requisitos

- Entorno virtual activo
- Variables de entorno configuradas (`.env`) o exportadas en la terminal
- Schema y datos base aplicados (`bari_lms_postgresql.sql` + bootstrap automático)

## Ejecución

Desde la raíz del proyecto:

```bash
# Todos los seeds en orden (recomendado)
python database/seeds/run_all.py

# O individualmente, en orden
python database/seeds/01_estructura.py
python database/seeds/02_instructores.py
python database/seeds/03_aprendices.py
```

Los seeds son **idempotentes**: se pueden ejecutar varias veces sin duplicar datos.

---

## Qué crea cada seed

| Archivo | Contenido |
|---|---|
| `01_estructura.py` | Catálogos (tipo documento, sexo), regional, centro, coordinación, red de conocimiento, área, niveles de formación, proyecto formativo con 4 fases, programa ADSO |
| `02_instructores.py` | 3 instructores completos (usuario → persona → instructor → perfil) y una ficha asignada a cada uno |
| `03_aprendices.py` | 6 aprendices (usuario → persona → aprendiz → perfil), 2 empresas EP e inscripciones en fichas con estados variados |

---

## Cuentas de prueba

Contraseña de todas: **`Sena2024*`**

### Instructores

| Correo | Ficha asignada |
|---|---|
| `juan.perez@sena.edu.co` | 2900001 |
| `maria.lopez@sena.edu.co` | 2900002 |
| `carlos.rodriguez@sena.edu.co` | 2900003 |

### Aprendices

| Correo | Ficha | Estado |
|---|---|---|
| `ana.gomez@aprendiz.sena.edu.co` | 2900001 | Etapa lectiva |
| `luis.torres@aprendiz.sena.edu.co` | 2900001 | En etapa productiva (TechSoft SAS) |
| `sofia.mendez@aprendiz.sena.edu.co` | 2900002 | Etapa lectiva |
| `andres.ruiz@aprendiz.sena.edu.co` | 2900002 | En etapa productiva (Innovatech Ltda) |
| `camila.vargas@aprendiz.sena.edu.co` | 2900003 | Etapa lectiva |
| `miguel.castro@aprendiz.sena.edu.co` | 2900003 | Lectiva concluida, pendiente EP |

---

## Diagnóstico

Si algo no funciona, ejecuta el script de diagnóstico para verificar la cadena de datos:

```bash
python database/seeds/diagnostico.py
```

Muestra `✓` o `✗` por cada eslabón (usuario → perfil → persona → instructor → ficha).
