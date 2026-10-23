"""
Plantilla de configuración secreta para la conexión a PostgreSQL.

NOTA: si prefieres usar un archivo .env en la raíz del proyecto (modelo:
.env.example), no necesitas este archivo; el .env tiene prioridad.

INSTRUCCIONES DE USO
--------------------
1. Copia este archivo con el nombre  src/secret_config.py
       (Windows)      copy src\secret_config_sample.py src\secret_config.py
       (Linux / Mac)  cp src/secret_config_sample.py src/secret_config.py
2. Abre src/secret_config.py y reemplaza los valores de ejemplo por los
   de tu base de datos. En Render los encuentras en tu instancia de
   PostgreSQL, sección "Connections" (usa los datos de conexión EXTERNA
   si ejecutas el programa desde tu computador).
3. NUNCA subas secret_config.py a GitHub: ya está en el .gitignore.
   Este archivo (secret_config_sample.py) sí se sube, pero SIN datos reales.

Significado de cada variable
----------------------------
DB_USER      Usuario de la base de datos.
DB_PASSWORD  Contraseña del usuario.
DB_HOST      Servidor. En Render: dpg-xxxxxxxx-a.<region>-postgres.render.com
DB_PORT      Puerto (PostgreSQL usa 5432 por defecto).
DB_NAME      Base de datos que usa el programa.
DB_NAME_TEST Base de datos SOLO para las pruebas unitarias. Su nombre debe
             terminar en "_test" porque las pruebas crean y borran tablas.
DB_SSLMODE   "require" para Render (exige SSL); "prefer" para un
             PostgreSQL local sin SSL.
"""

DB_USER = "tu_usuario"
DB_PASSWORD = "tu_contraseña"
DB_HOST = "dpg-xxxxxxxxxxxx-a.<region>-postgres.render.com"
DB_PORT = 5432
DB_NAME = "liquidacion"
DB_NAME_TEST = "liquidacion_test"
DB_SSLMODE = "require"
