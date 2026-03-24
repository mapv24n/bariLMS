# Migraciones — bariLMS

> **Nota para IAs (Claude y similares):** antes de modificar el schema,
> ejecuta `database/query.py` con Bash para verificar el estado real de la BD.
> Usa `dbmate status` para saber que migraciones estan aplicadas.
> Crea siempre una nueva migracion en `database/migrations/` — nunca
> edites el archivo `bari_EtapaProductiva_postgresql.sql` directamente
> para alterar tablas existentes en produccion.

Herramienta: **[Dbmate](https://github.com/amacneil/dbmate)**
Base de datos: PostgreSQL
Alcance actual: módulo Etapa Productiva (`empresa`, `ficha_aprendiz`, `contrato_aprendizaje`)

---

## Instalación de Dbmate

### Windows (recomendado: Scoop)
```powershell
scoop install dbmate
```

### Windows (manual)
Descarga el binario desde [github.com/amacneil/dbmate/releases](https://github.com/amacneil/dbmate/releases)
→ `dbmate-windows-amd64.exe`, renómbralo a `dbmate.exe` y agrégalo al PATH.

### Mac / Linux
```bash
brew install dbmate          # Mac
sudo apt install dbmate      # Debian/Ubuntu (si está en repos)
# o descarga el binario directamente
```

---

## Configuración

Dbmate necesita `DATABASE_URL`. Agrégala a tu `.env`:

```env
DATABASE_URL=postgres://postgres:tu_password@127.0.0.1:5432/bari_lms
```

Si ya tienes las variables `PG*` en tu `.env`, también puedes pasar la URL directamente
en cada comando (ver sección Comandos).

---

## Comandos

Ejecutar siempre desde la **raíz del proyecto**.

```bash
# Aplicar todas las migraciones pendientes
dbmate --migrations-dir database/migrations up

# Revertir la última migración aplicada
dbmate --migrations-dir database/migrations down

# Ver estado (qué está aplicado / pendiente)
dbmate --migrations-dir database/migrations status

# Crear una nueva migración
dbmate --migrations-dir database/migrations new nombre_descriptivo
# → crea database/migrations/<timestamp>_nombre_descriptivo.sql

# Usando URL explícita (sin DATABASE_URL en .env)
dbmate --url "postgres://postgres:pass@127.0.0.1:5432/bari_lms" \
       --migrations-dir database/migrations up
```

> Dbmate registra las migraciones aplicadas en la tabla `schema_migrations` de tu base de datos.

---

## Estructura de un archivo de migración

```sql
-- migrate:up

CREATE TABLE IF NOT EXISTS nueva_tabla (
    id UUID PRIMARY KEY,
    ...
);

-- migrate:down

DROP TABLE IF EXISTS nueva_tabla;
```

---

## Migraciones actuales

| Archivo | Descripción |
|---|---|
| `20260323000001_initial_etapa_productiva.sql` | Crea `empresa`, `ficha_aprendiz`, `contrato_aprendizaje` con índices y constraints |

---

## Primer uso (DB ya existe)

Si las tablas EP ya están creadas en tu base de datos, marca la migración como aplicada
sin ejecutarla:

```bash
dbmate --migrations-dir database/migrations dump   # opcional: exporta el schema actual
dbmate --migrations-dir database/migrations up     # aplica solo las pendientes
```

Dbmate usa `CREATE TABLE IF NOT EXISTS`, así que si las tablas ya existen simplemente
no las vuelve a crear.
