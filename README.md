# Riza tus Rizos — Sistema de Gestión de Inventario

Proyecto académico de aplicación web para apoyar el control interno de inventario de **Riza tus Rizos**, con seguimiento de productos, lotes, existencias y movimientos de entrada y salida.

> **Estado del proyecto:** en desarrollo. Algunas funcionalidades y pruebas todavía requieren integración y validación. Este repositorio **no** corresponde a una versión lista para producción.

## Objetivo

Centralizar la información del inventario, facilitar la consulta de existencias por producto y lote, y mejorar la trazabilidad de los movimientos y el seguimiento de vencimientos.

El alcance inicial es **interno**: no incluye tienda pública, carrito de compras ni pagos en línea.

## Tecnologías y herramientas

- **Backend:** Python y Django.
- **Base de datos objetivo:** PostgreSQL.
- **Interfaz:** plantillas HTML y CSS.
- **Control de versiones:** Git y GitHub, mediante ramas y pull requests.
- **Gestión del trabajo:** Taiga, con planificación Scrum y visualización Kanban.
- **Configuración local:** `python-dotenv` para cargar variables de entorno, según la configuración del proyecto.

## Historias de usuario

| Código | Funcionalidad |
|---|---|
| HU-001 | Gestionar productos |
| HU-002 | Consultar inventario |
| HU-003 | Registrar entradas de inventario |
| HU-004 | Registrar salidas de inventario |
| HU-005 | Gestionar lotes y vencimientos |
| HU-006 | Alertas de vencimiento |
| HU-007 | Alertas de stock bajo |
| HU-008 | Consultar historial de movimientos |
| HU-009 | Inicio de sesión y autenticación |

Estas historias forman parte del backlog. **Estar registrada una historia no significa que su implementación esté terminada.** El estado vigente se consulta en Taiga y se valida con las pruebas y pull requests correspondientes.

## Estructura de referencia

La estructura puede variar entre ramas a medida que el equipo integra funcionalidades:

```text
Proyecto-Integrado/
├── config/                         # Configuración y rutas de Django
├── inventario/                     # App de inventario
│   ├── migrations/                 # Migraciones de modelos
│   ├── templates/                  # Plantillas HTML
│   │   ├── alertas.html
│   │   ├── inicio.html
│   │   └── inventario/
│   │       └── base.html
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── servicios_vencimientos.py  # Clasificación/consulta de vencimientos
│   ├── tests.py
│   ├── test_vencimientos.py        # Si está incorporado en la rama
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Modelo de datos observado en el desarrollo

La aplicación de inventario incluye modelos para **Categoría**, **Unidad de medida**, **Producto**, **Lote**, **Entrada** y **Salida**. Los movimientos de entrada y salida se vinculan a productos, lotes y usuarios responsables. Los nombres y relaciones definitivos deben revisarse antes de integrar ramas y aplicar migraciones.

**Diferencia importante:** el estado administrativo de un producto (`esta_activo`) no equivale a su estado de existencias (`disponible`, `stock_bajo` o `sin_stock`). Un producto sin stock puede continuar activo.

## Instalación local

### Requisitos

- Python compatible con las dependencias registradas en `requirements.txt`.
- Git.
- PostgreSQL instalado y disponible **si la rama está configurada para usarlo**.

### 1. Clonar el repositorio

```powershell
git clone https://github.com/N1k0-Bellic/Proyecto-Integrado.git
cd Proyecto-Integrado
```

La rama principal puede no incluir funcionalidades que todavía estén en desarrollo en otras ramas. Para trabajar en una historia concreta, revisa las ramas disponibles:

```powershell
git fetch origin
git branch -a
```

### 2. Crear y activar el entorno virtual (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

Si aparece `ModuleNotFoundError: No module named 'dotenv'`, comprueba que **`python-dotenv`** esté incluido en `requirements.txt` e instalado en el entorno virtual activo. El paquete se instala como `python-dotenv` y se importa como `dotenv`.

### 4. Configurar las variables de entorno y PostgreSQL

Revisa `config/settings.py` para identificar **los nombres exactos de las variables de entorno** que espera la rama descargada. Crea un archivo `.env` local con los valores correspondientes y configura una base de datos PostgreSQL accesible.

**No subas `.env`, contraseñas, claves secretas ni credenciales a GitHub.** No se incluye aquí una plantilla de variables porque sus nombres deben corresponder a la configuración real de `settings.py`.

### 5. Verificar y preparar la base de datos

```powershell
python manage.py check
python manage.py migrate
```

Antes de ejecutar migraciones en una base de datos compartida, coordina con el equipo las migraciones pendientes de cada rama.

### 6. Iniciar el servidor

```powershell
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` y consulta las rutas efectivamente registradas en `config/urls.py` e `inventario/urls.py`. **No todas las rutas están necesariamente disponibles en todas las ramas.**

## Alertas de vencimiento (HU-006)

La lógica propuesta clasifica cada lote a partir de su fecha de vencimiento, evaluada respecto de la fecha local actual:

| Clasificación | Regla propuesta |
|---|---|
| Vencido | Fecha anterior a hoy |
| Vence hoy | Fecha igual a hoy |
| Próximo a vencer | Entre 1 y 30 días restantes |
| Vigente | Más de 30 días restantes |
| Sin fecha | No existe fecha de vencimiento registrada |

El **plazo de 30 días es provisional** y debe validarse con Riza tus Rizos. El tratamiento operativo de un producto que vence hoy también requiere validación. La consulta de alertas no debe eliminar automáticamente las existencias físicas de los lotes vencidos.

El archivo `inventario/servicios_vencimientos.py` contiene la lógica de clasificación/consulta desarrollada para esta historia, según la rama correspondiente. La integración completa con las plantillas y la base de datos debe comprobarse mediante pruebas.

## Pruebas

Para ejecutar las pruebas de la aplicación:

```powershell
python manage.py test inventario --verbosity=2
```

Si la rama contiene `inventario/test_vencimientos.py`, las pruebas de vencimiento pueden ejecutarse por separado:

```powershell
python manage.py test inventario.test_vencimientos --verbosity=2
```

**Estado de validación:** durante el desarrollo se detectaron pruebas de `ProductoStockTest` que esperaban activar o desactivar productos automáticamente según su stock. Esa expectativa debe conciliarse con la regla administrativa antes de considerar la suite completa aprobada. No se debe informar `OK` sin haber ejecutado y verificado las pruebas en la rama correspondiente.

Django puede crear una base de datos temporal para las pruebas; su usuario de PostgreSQL debe contar con los permisos necesarios.

## Flujo de trabajo colaborativo

1. Actualizar la rama de trabajo desde la base acordada por el equipo.
2. Desarrollar cada historia en una rama independiente, por ejemplo `feature/hu-006-alertas-vencimiento`.
3. Ejecutar verificaciones y pruebas aplicables.
4. Crear commits descriptivos y subir la rama.
5. Abrir un **pull request** para revisión; utilizar **Draft** si aún faltan pruebas o integración.
6. Integrar a `main` únicamente después de revisar conflictos, criterios de aceptación y resultados de pruebas.

No incluir archivos temporales como `resultado_pruebas.txt`, entornos virtuales o secretos en los commits.

## Definition of Done (propuesta)

Una historia o tarea se considera terminada cuando:

- Cumple sus criterios de aceptación.
- El código está versionado y revisado.
- Las pruebas pertinentes se han ejecutado con resultados documentados.
- No existen errores críticos conocidos que impidan su uso previsto.
- Se adjuntan o enlazan evidencias en Taiga.
- La integración con los componentes dependientes está verificada, cuando corresponda.

## Seguimiento y próximos pasos

El equipo usa **Scrum** para planificar entregas y **Kanban en Taiga** para visualizar el avance. Las presentaciones de seguimiento definidas son **26 de noviembre y 3 de diciembre de 2026**.

Prioridades de integración:

- Acordar y verificar los modelos compartidos de productos, lotes y movimientos.
- Integrar las consultas de inventario y alertas con PostgreSQL.
- Resolver las pruebas inconsistentes sobre estado administrativo y stock.
- Validar los permisos y la autenticación antes de utilizar datos reales.
- Confirmar los criterios de vencimiento y niveles mínimos de existencias con la empresa.

---

**Proyecto académico en desarrollo.** La documentación se actualizará a medida que se aprueben historias, se integren pull requests y se confirmen reglas de negocio.
