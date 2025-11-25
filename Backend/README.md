# Sistema de Justificación de Inasistencias

Sistema web completo para la gestión de justificaciones de inasistencias académicas desarrollado con Flask y Python.

## Características Principales

### Dashboard Administrativo
- Métricas en tiempo real de solicitudes y estudiantes
- Visualización de solicitudes recientes
- Estadísticas de aprobación y tiempos de respuesta
- Alertas de estudiantes en riesgo

### Gestión de Justificaciones
- Visualización de todas las solicitudes con filtros por estado
- Detalles completos de cada solicitud
- Aprobación/rechazo de solicitudes
- Gestión de archivos adjuntos
- Búsqueda por estudiante

### Gestión de Estudiantes
- CRUD completo de estudiantes
- Perfil detallado con información académica y personal
- Seguimiento de asistencia y porcentajes
- Historial de justificaciones por estudiante
- Estados: Activo/Inactivo
- Identificación de estudiantes en riesgo

### Reportes y Análisis
- Tendencias mensuales de solicitudes
- Distribución de motivos de justificación
- Reportes de asistencia por niveles de riesgo
- Métricas de rendimiento del sistema
- Estudiantes que requieren atención

## Tecnologías Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-Migrate
- **Base de Datos**: SQLite (desarrollo) / Oracle (producción)
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **UI Framework**: Bootstrap 5
- **Iconos**: Font Awesome
- **Gráficos**: Chart.js

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd sistema-justificaciones
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno** (opcional)
```bash
# Crear archivo .env
DATABASE_URL=sqlite:///justifications.db
SECRET_KEY=tu-clave-secreta-aqui
```

6. **Inicializar base de datos**
```bash
python init_db.py
```

7. **Ejecutar la aplicación**
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
sistema-justificaciones/
├── app/
│   ├── models/           # Modelos de datos
│   │   ├── student_extended.py
│   │   ├── justification.py
│   │   └── admin.py
│   ├── routes/           # Rutas/Endpoints
│   │   ├── dashboard_routes.py
│   │   ├── justification_routes.py
│   │   ├── student_extended_routes.py
│   │   └── web_routes.py
│   ├── services/         # Lógica de negocio
│   │   ├── justification_service.py
│   │   └── student_extended_service.py
│   ├── templates/        # Plantillas HTML
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── justifications.html
│   ├── __init__.py       # Configuración de la app
│   └── settings.py       # Configuraciones
├── uploads/              # Archivos subidos
├── init_db.py           # Script de inicialización
├── run.py               # Punto de entrada
└── requirements.txt     # Dependencias
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/admin` - Datos del dashboard administrativo
- `GET /api/dashboard/reports` - Dashboard de reportes
- `GET /api/dashboard/students-management` - Dashboard de estudiantes

### Justificaciones
- `GET /api/justifications` - Listar justificaciones con filtros
- `GET /api/justifications/<id>` - Detalles de una justificación
- `POST /api/justifications/<id>/approve` - Aprobar justificación
- `POST /api/justifications/<id>/reject` - Rechazar justificación
- `POST /api/justifications/create` - Crear nueva justificación

### Estudiantes
- `GET /api/students` - Listar estudiantes con filtros
- `GET /api/students/<id>` - Detalles de un estudiante
- `POST /api/students/create` - Crear nuevo estudiante
- `PUT /api/students/<id>/update` - Actualizar estudiante
- `DELETE /api/students/<id>/delete` - Desactivar estudiante

### Reportes
- `GET /api/justifications/reports/monthly-trends` - Tendencias mensuales
- `GET /api/justifications/reports/reason-distribution` - Distribución de motivos
- `GET /api/students/attendance-report` - Reporte de asistencia

## Datos de Prueba

El sistema incluye datos de ejemplo que se crean automáticamente:

### Usuario Administrador
- **Usuario**: admin
- **Contraseña**: admin123
- **Email**: admin@vallegrande.edu.pe

### Estudiantes de Ejemplo
- María González Pérez (67584920)
- Carlos Rodríguez Silva (2024001235)
- José Manuel Vega (58721694) - En riesgo
- Ana Lucía Torres (2024001236)
- Roberto Castillo Herrera (2024001239) - En riesgo

## Configuración para Producción

Para usar Oracle en producción, descomenta y configura las variables en `app/settings.py`:

```python
# Variables de entorno requeridas
DB_USER=tu_usuario_oracle
DB_PASS=tu_password_oracle
DB_TNS_NAME=tu_dsn_oracle
DB_WALLET_DIR=ruta_al_wallet
```