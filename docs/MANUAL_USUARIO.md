# Manual de Usuario - ConciliaPyme Ledger Pro

## Versión 2.3.0

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Primeros Pasos](#primeros-pasos)
4. [Módulos Principales](#módulos-principales)
5. [Funcionalidades Avanzadas](#funcionalidades-avanzadas)
6. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

**ConciliaPyme Ledger Pro** es una aplicación de escritorio para conciliación financiera automatizada, diseñada específicamente para PYMES paraguayas. Utiliza tecnología blockchain para generar evidencia criptográfica inmutable de todas las operaciones.

### Características Principales

- ✅ Importación múltiple de formatos (CSV, MT940, CAMT.053, SIFEN)
- ✅ Conciliación automática inteligente
- ✅ Ledger blockchain local con verificación criptográfica
- ✅ Auditoría con hash encadenado
- ✅ Cotización USD/PYG en tiempo real
- ✅ Backup cifrado
- ✅ Múltiples usuarios con roles
- ✅ Temas visuales personalizables

---

## Instalación

### Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.8 o superior
- **RAM**: 4 GB mínimo
- **Espacio en disco**: 500 MB

### Instalación Paso a Paso

1. **Descargar la aplicación**
   - Copie la carpeta completa a su equipo

2. **Ejecutar la aplicación**
   ```
   Doble click en run_app.bat
   ```

3. **Credenciales por defecto**
   - Usuario: `admin`
   - Contraseña: `Admin@2026!`

---

## Primeros Pasos

### Inicio de Sesión

1. Ingrese su usuario y contraseña
2. Presione "Iniciar Sesión" o Enter
3. Tras 5 intentos fallidos, la cuenta se bloquea por 15 minutos

### Dashboard Principal

Al ingresar, verá el panel principal con:

- **Métricas clave**: Ventas, movimientos, conciliaciones
- **Accesos rápidos**: Botones para operaciones comunes
- **Selector de tema**: Claro, Oscuro o Sistema

### Cargar Datos Demo

Para probar la aplicación:

1. Vaya al Dashboard
2. Click en "Cargar Datos Demo"
3. Los datos de ejemplo se cargarán automáticamente

---

## Módulos Principales

### 1. Importar Datos

**Formatos soportados:**

| Formato | Descripción | Extensión |
|---------|-------------|-----------|
| CSV Ventas | Planilla de ventas | .csv |
| CSV Banco | Extracto bancario | .csv |
| MT940 | Standard bancario internacional | .txt |
| CAMT.053 | XML bancario SEPA | .xml |
| SIFEN/DTE | Facturación electrónica Paraguay | .xml |

**Pasos para importar:**

1. Seleccione el tipo de archivo
2. Elija el preset bancario (si aplica)
3. Click en "Seleccionar Archivo"
4. Click en "Importar"
5. Revise el log de importación

### 2. Conciliación

**Estados posibles:**

- 🟢 **Conciliada**: Coincidencia exacta o muy cercana
- 🟡 **Discrepancia**: Diferencias menores detectadas
- 🔴 **Pendiente**: Sin coincidencia encontrada

**Reglas de conciliación:**

1. Comparación por referencia
2. Coincidencia cliente/descripción
3. Tolerancia de fecha (configurable)
4. Tolerancia de monto (configurable)

**Para ejecutar:**

1. Vaya a la pestaña "Conciliación"
2. Revise la configuración actual
3. Click en "Ejecutar Conciliación"
4. Revise resultados en la tabla
5. Click en "Guardar Resultados"

### 3. Historial

**Funcionalidades:**

- Listado de corridas anteriores
- Código único por corrida (CONC-YYYYMMDD-HHMMSS)
- Doble click para cargar resultados previos
- Posibilidad de re-exportar

### 4. Cotización USD/PYG

**Fuentes disponibles:**

- BCP (Banco Central del Paraguay)
- SET
- Banco Familiar
- Cambios Chaco

**Características:**

- Actualización automática desde API
- Caché local si no hay conexión
- Conversor USD → PYG integrado
- Fecha de actualización visible

### 5. Auditoría

**Eventos registrados:**

- Logins exitosos y fallidos
- Importaciones de datos
- Ejecuciones de conciliación
- Exportaciones de reportes
- Verificaciones de ledger
- Backups creados/restaurados

**Verificación de integridad:**

Cada evento está encadenado criptográficamente mediante hashes SHA-256. Para verificar:

1. Vaya a la pestaña "Auditoría"
2. Click en "Verificar Integridad"
3. El sistema validará toda la cadena

---

## Funcionalidades Avanzadas

### Gestión de Usuarios

**Roles disponibles:**

| Rol | Permisos |
|-----|----------|
| Admin | Todos los permisos, gestión de usuarios |
| Contador | Operaciones diarias, conciliación |
| Gerente | Consultas, reportes, aprobación |
| Auditor | Solo lectura, verificaciones |

**Crear nuevo usuario:**

1. Menú Herramientas → Usuarios
2. Click en "Nuevo Usuario"
3. Complete los campos requeridos
4. La contraseña debe cumplir política de seguridad:
   - Mínimo 10 caracteres
   - Al menos 1 mayúscula
   - Al menos 1 minúscula
   - Al menos 1 número
   - Al menos 1 símbolo especial

### Configuración de Empresa

**Datos configurables:**

- Nombre de empresa
- RUC
- Sucursal
- Titular de licencia

**Generar licencia demo:**

1. Herramientas → Configuración Empresa
2. Complete datos básicos
3. Click en "Generar Licencia Demo"
4. La licencia tendrá validez de 30 días

### Backup y Restauración

**Crear backup:**

1. Menú Archivo → Backup
2. Seleccione ubicación de guardado
3. Ingrese clave de cifrado
4. El archivo se guardará con extensión `.cplybak`

**Restaurar backup:**

1. Menú Archivo → Restaurar Backup
2. Seleccione archivo `.cplybak`
3. Ingrese la clave de cifrado
4. Reinicie la aplicación

⚠️ **Importante**: Sin la clave correcta, no se puede restaurar el backup.

### Integración Hyperledger Fabric

**Exportar payload:**

1. Ejecute una conciliación
2. En la pestaña Conciliación
3. Click en "Exportar Payload Fabric"
4. Use el JSON generado con el chaincode

Para más detalles, consulte `fabric/README_FABRIC.md`

### Reportes y Exportación

**Formatos de exportación:**

- **JSON**: Reporte completo con métricas, resultados y ledger
- **CSV**: Tabla de resultados para Excel

**Contenido del JSON:**

```json
{
  "app": "ConciliaPyme Ledger Pro",
  "version": "2.3.0",
  "timestamp": "2026-01-15T10:30:00",
  "user": "admin",
  "metrics": {...},
  "rules": {...},
  "last_run": {...},
  "results": [...],
  "recent_ledger": [...]
}
```

---

## Solución de Problemas

### La aplicación no inicia

**Posibles causas:**
- Python no instalado
- Versión de Python incompatible

**Solución:**
```bash
python --version
# Debe mostrar Python 3.8.x o superior
```

### Error de login

**Causas:**
- Contraseña incorrecta
- Cuenta bloqueada

**Solución:**
- Espere 15 minutos si está bloqueada
- Use las credenciales por defecto: admin / Admin@2026!

### No se pueden importar archivos

**Verifique:**
- El formato del archivo sea correcto
- Las columnas coincidan con el formato esperado
- El archivo no esté corrupto

### Error de cotización

**Si la API no responde:**
- El sistema usará automáticamente el caché local
- Intente nuevamente más tarde

### Ledger muestra error de integridad

**Posible causa:**
- Manipulación manual de la base de datos

**Solución:**
- Restaure desde backup válido
- Contacte al administrador

---

## Contacto y Soporte

Para asistencia técnica:
- Email: soporte@conciliapyme.com.py
- Documentación adicional en `/docs`

---

Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.
