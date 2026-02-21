# Database Setup - mnemos

Esta guía te ayudará a configurar la base de datos para **mnemos**, ya sea SQLite (para desarrollo) o PostgreSQL (para producción).

## Tabla de Contenidos

- [Configuración Rápida](#configuración-rápida)
- [SQLite (Desarrollo)](#sqlite-desarrollo)
- [PostgreSQL (Producción)](#postgresql-producción)
  - [Instalación Local](#instalación-local-postgresql)
  - [Con Docker](#con-docker)
  - [Servicios Cloud](#servicios-cloud)
- [Migración de SQLite a PostgreSQL](#migración-de-sqlite-a-postgresql)
- [Troubleshooting](#troubleshooting)

---

## Configuración Rápida

**mnemos** usa la variable de entorno `DB_TYPE` para controlar qué base de datos usar:

```bash
# SQLite (por defecto)
DB_TYPE=sqlite

# PostgreSQL
DB_TYPE=postgresql
```

### Cambiar entre SQLite y PostgreSQL

Solo necesitas cambiar `DB_TYPE` en tu archivo `.env`:

**Para SQLite (desarrollo):**
```bash
DB_TYPE=sqlite
SQLITE_PATH=./db.sqlite3
```

**Para PostgreSQL (producción):**
```bash
DB_TYPE=postgresql
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db
```

---

## SQLite (Desarrollo)

### Ventajas
✅ Sin instalación adicional (incluido en Python)  
✅ Configuración cero  
✅ Perfecto para desarrollo local  
✅ Archivo único fácil de respaldar  

### Configuración

**1. Archivo `.env`:**
```bash
DB_TYPE=sqlite
SQLITE_PATH=./db.sqlite3
```

**2. Iniciar aplicación:**
```bash
uv run uvicorn main:app --reload
```

La base de datos `db.sqlite3` se creará automáticamente en el directorio raíz.

### Backup SQLite

```bash
# Crear backup
cp db.sqlite3 backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Restaurar backup
cp backups/db_20260220_100000.sqlite3 db.sqlite3
```

---

## PostgreSQL (Producción)

### Ventajas
✅ Mejor rendimiento para alta concurrencia  
✅ Escalable  
✅ Soporte avanzado de tipos de datos  
✅ Recomendado para producción  

### Instalación Local (PostgreSQL)

#### macOS (Homebrew)

```bash
# Instalar PostgreSQL
brew install postgresql@16

# Iniciar servicio
brew services start postgresql@16

# Verificar instalación
psql --version
```

#### Ubuntu/Debian

```bash
# Actualizar paquetes
sudo apt update

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar estado
sudo systemctl status postgresql
```

#### Windows

Descarga el instalador desde: https://www.postgresql.org/download/windows/

### Configurar Base de Datos

**1. Conectar a PostgreSQL:**

```bash
# macOS/Linux
sudo -u postgres psql

# Windows (desde PowerShell como administrador)
psql -U postgres
```

**2. Crear base de datos y usuario:**

```sql
-- Crear usuario
CREATE USER mnemos_user WITH PASSWORD 'tu_contraseña_segura';

-- Crear base de datos
CREATE DATABASE mnemos_db OWNER mnemos_user;

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE mnemos_db TO mnemos_user;

-- Salir
\q
```

**3. Verificar conexión:**

```bash
psql -U mnemos_user -d mnemos_db -h localhost
```

**4. Actualizar `.env`:**

```bash
DB_TYPE=postgresql
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db
```

**5. Iniciar aplicación:**

```bash
uv run uvicorn main:app --reload
```

Las tablas se crearán automáticamente al iniciar la aplicación.

---

## Con Docker

### Docker Compose

Crea `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: mnemos_postgres
    environment:
      POSTGRES_USER: mnemos_user
      POSTGRES_PASSWORD: tu_contraseña_segura
      POSTGRES_DB: mnemos_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mnemos_user -d mnemos_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Opcional: Adminer para gestión visual de BD
  adminer:
    image: adminer:latest
    container_name: mnemos_adminer
    ports:
      - "8080:8080"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

**Iniciar PostgreSQL:**

```bash
docker-compose up -d postgres
```

**Actualizar `.env`:**

```bash
DB_TYPE=postgresql
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db
```

**Acceder a Adminer (opcional):**

Abre http://localhost:8080 y usa las credenciales:
- System: PostgreSQL
- Server: postgres
- Username: mnemos_user
- Password: tu_contraseña_segura
- Database: mnemos_db

---

## Servicios Cloud

### Supabase (Gratis)

1. Crea cuenta en https://supabase.com
2. Crea un nuevo proyecto
3. Ve a "Settings" → "Database"
4. Anota las credenciales: host, database, user, password
5. Actualiza `.env`:

```bash
DB_TYPE=postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[TU_CONTRASEÑA]
POSTGRES_HOST=db.[PROYECTO].supabase.co
POSTGRES_PORT=5432
POSTGRES_DB=postgres
```

### Neon (Gratis)

1. Crea cuenta en https://neon.tech
2. Crea un nuevo proyecto
3. Anota las credenciales de conexión
4. Actualiza `.env`:

```bash
DB_TYPE=postgresql
POSTGRES_USER=[usuario]
POSTGRES_PASSWORD=[contraseña]
POSTGRES_HOST=[host].neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=[database]
```

### Railway (Gratis con límites)

1. Crea cuenta en https://railway.app
2. Crea nuevo proyecto → Add PostgreSQL
3. Ve a "Connect" → Variables
4. Actualiza `.env`:

```bash
DB_TYPE=postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[contraseña]
POSTGRES_HOST=[host].railway.app
POSTGRES_PORT=[puerto]
POSTGRES_DB=railway
```

---

## Migración de SQLite a PostgreSQL

### Opción 1: Manual (Pequeñas bases de datos)

**1. Exportar datos desde SQLite:**

```bash
sqlite3 db.sqlite3 .dump > backup.sql
```

**2. Limpiar archivo SQL:**

Editar `backup.sql` y eliminar líneas incompatibles:
- `PRAGMA foreign_keys=OFF;`
- `BEGIN TRANSACTION;`
- `COMMIT;`

**3. Importar a PostgreSQL:**

```bash
psql -U mnemos_user -d mnemos_db -h localhost < backup.sql
```

### Opción 2: pgloader (Recomendado)

**Instalar pgloader:**

```bash
# macOS
brew install pgloader

# Ubuntu/Debian
sudo apt install pgloader
```

**Migrar:**

```bash
pgloader db.sqlite3 postgresql://mnemos_user:contraseña@localhost:5432/mnemos_db
```

### Opción 3: Python Script

Crea `migrate.py`:

```python
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Conexión SQLite
sqlite_conn = sqlite3.connect('db.sqlite3')
sqlite_cur = sqlite_conn.cursor()

# Conexión PostgreSQL
pg_conn = psycopg2.connect(
    "postgresql://mnemos_user:contraseña@localhost:5432/mnemos_db"
)
pg_cur = pg_conn.cursor()

# Obtener todas las tablas
sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [table[0] for table in sqlite_cur.fetchall() if table[0] != 'sqlite_sequence']

for table in tables:
    print(f"Migrando tabla: {table}")
    
    # Obtener datos
    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()
    
    if rows:
        # Obtener columnas
        sqlite_cur.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insertar en PostgreSQL
        cols = ', '.join(columns)
        query = f"INSERT INTO {table} ({cols}) VALUES %s ON CONFLICT DO NOTHING"
        execute_values(pg_cur, query, rows)

pg_conn.commit()
pg_cur.close()
pg_conn.close()
sqlite_cur.close()
sqlite_conn.close()

print("Migración completada!")
```

**Ejecutar:**

```bash
python migrate.py
```

---

## Troubleshooting

### Error: "could not connect to server"

**Causa:** PostgreSQL no está corriendo

**Solución:**
```bash
# macOS
brew services start postgresql@16

# Linux
sudo systemctl start postgresql

# Docker
docker-compose up -d postgres
```

### Error: "password authentication failed"

**Causa:** Credenciales incorrectas

**Solución:**
1. Verifica `.env` tenga las credenciales correctas
2. Resetea contraseña en PostgreSQL:

```sql
ALTER USER mnemos_user WITH PASSWORD 'nueva_contraseña';
```

### Error: "database does not exist"

**Causa:** Base de datos no creada

**Solución:**
```bash
psql -U postgres
CREATE DATABASE mnemos_db OWNER mnemos_user;
\q
```

### Error: "relation does not exist"

**Causa:** Tablas no creadas

**Solución:**
La aplicación crea las tablas automáticamente al iniciar. Reinicia:
```bash
uv run uvicorn main:app --reload
```

### Verificar conexión PostgreSQL

```bash
# Ver bases de datos
psql -U postgres -c "\l"

# Ver tablas en mnemos_db
psql -U mnemos_user -d mnemos_db -c "\dt"

# Ver conexiones activas
psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE datname='mnemos_db';"
```

### Backup PostgreSQL

```bash
# Crear backup
pg_dump -U mnemos_user -d mnemos_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
psql -U mnemos_user -d mnemos_db < backup_20260220_100000.sql
```

---

## Recomendaciones de Producción

1. **Usar PostgreSQL** en lugar de SQLite
2. **Variables de entorno seguras**: No hardcodear contraseñas
3. **Backups automáticos**: Usar pg_dump con cron/scripts
4. **Conexiones pooling**: Configurar `DB_POOL_SIZE` y `DB_MAX_OVERFLOW`
5. **SSL/TLS**: Activar conexiones encriptadas
6. **Monitoreo**: Usar herramientas como pg_stat_statements

### Variables de Configuración Avanzada

El sistema ya viene configurado con connection pooling para PostgreSQL. Puedes ajustar estos valores en `.env`:

```bash
DB_TYPE=postgresql

# Credenciales
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db

# Connection Pool (opcional)
DB_POOL_SIZE=10        # Conexiones en pool (default: 10)
DB_MAX_OVERFLOW=20     # Conexiones extra permitidas (default: 20)
```

El código en `database.py` automáticamente:
- Aplica `pool_pre_ping=True` para verificar conexiones antes de usar
- Recicla conexiones cada hora (`pool_recycle=3600`)
- Usa las configuraciones óptimas según el tipo de BD

---

## Referencias

- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database)
- [pgloader Migration Tool](https://pgloader.io/)
