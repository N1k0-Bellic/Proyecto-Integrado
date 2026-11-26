# Guía de Configuración del Entorno: Neon Cloud (PostgreSQL) + Django 

**Proyecto: Sistema de Inventario "Riza tus Rizos"** 

Se ha migrado la base de datos de PostgreSQL a la nube mediante Neon Cloud para que todo el equipo comparta un entorno centralizado sin necesidad de instalar motores de base de datos ni configurar pgAdmin en sus computadoras. Sigue estos pasos para activar tu entorno al clonar o actualizar el repositorio: 

## **1. Requisitos Previos** 

Asegúrate de tener instalado únicamente lo siguiente en tu computadora: 

- Python (versión 3.10 o superior recomendada). 

- Git para el control de versiones. 

_Nota: Ya NO es necesario instalar PostgreSQL ni pgAdmin 4 de forma local._ 

## **2. Clonar el Repositorio y Activar Entorno Virtual** 

Abre tu terminal (o la consola de VS Code) y ejecuta: 


# 1. Clonar el proyecto (si aún no lo tienes)

git clone https://github.com/N1k0-Bellic/Proyecto-Integrado.git
cd Proyecto-Integrado


# 2. Si ya tenías el repositorio clonado, descarga los últimos cambios

git pull


# 3. Crear un entorno virtual para aislar las dependencias

python -m venv .venv


# 4. Activar el entorno virtual en PowerShell o CMD:

.venv\Scripts\activate


# 5. Instalar las librerías necesarias (Django, Psycopg, python-dotenv, dj-
database-url, etc.)

pip install -r requirements.txt


## **3. Configurar las Variables de Entorno (.env)** 

El archivo settings.py ya está configurado para leer automáticamente la conexión a la nube. Por seguridad, las credenciales de Neon nunca se suben a GitHub. 

1. En la raíz del proyecto, busca el archivo llamado .env.example. 

2. Duplica ese archivo y renombra la copia para que se llame solamente .env. 

3. Abre el archivo .env y pega la siguiente URL de conexión: 

DATABASE_URL=postgresql://usuario:password@host-de-neon.aws.neon.tech/neondb?sslmode=require 

_Nota: Debería quedar solo esa única línea de código, exactamente igual. El archivo .env ya está incluido en el .gitignore, así que puedes guardar tranquilamente sin riesgo de subir las credenciales al repositorio._ 

## **4. Verificar la Conexión y Migraciones** 

Como la base de datos está en la nube, las tablas principales ya fueron creadas. Sin embargo, ejecuta el siguiente comando para confirmar que tu entorno se conecta correctamente a Neon y <u>sincronizar cualquier migración pendiente:</u> 

python manage.py migrate

Si la conexión es exitosa, verás "No migrations to apply" o una lista de operaciones terminadas con [OK]. 

## **5. Acceso al Panel de Administración (Superusuario)** 

Al compartir todos la misma base de datos en la nube, ya existe un usuario administrador creado para /admin ( user: ****, pass: **** ). Solo ejecuta python manage.py createsuperuser si necesitas crear una cuenta personal adicional. 

## **6. Levantar el Servidor** 

Ejecuta el proyecto con: 

python manage.py runserver


Abre tu navegador y entra a http://127.0.0.1:8000/. Ya deberías ver el proyecto funcionando conectado directamente a la base de datos compartida en Neon Cloud. 

**Tip importante para el equipo:** Como ahora todos apuntamos a la misma base de datos en Neon Cloud, los registros de prueba que crees o elimines serán visibles para todo el equipo. Además, si alguien modifica los modelos en Django y hace commit, solo una persona debe ejecutar python manage.py migrate (los demás solo deberán hacer git pull). 

