# Manual de Usuario - ConciliaPyme Ledger Pro (v2.3.0)

Bienvenido a **ConciliaPyme Ledger Pro**, la solución líder de escritorio diseñada especialmente para PYMES paraguayas que automatiza la conciliación de movimientos bancarios frente a comprobantes de ventas, respaldado por un ledger criptográfico local inmutable tipo blockchain preparado para integrarse con redes de Hyperledger Fabric.

---

## 1. Credenciales Iniciales de Acceso

La aplicación está preconfigurada con un usuario administrador por defecto para su primer ingreso:
* **Usuario:** `admin`
* **Contraseña:** `Admin@2026!`

> 🔒 **Nota de Seguridad:** Tras el primer ingreso, se recomienda ir a la pestaña "Administrar Usuarios" para registrar su propia cuenta de usuario fuerte y desactivar o cambiar las credenciales del usuario `admin` inicial para garantizar la seguridad del sistema.

---

## 2. Flujo de Trabajo Principal (Paso a Paso)

### Paso 2.1: Iniciar Sesión y Cargar Datos de Prueba
1. Inicie la aplicación mediante el archivo ejecutable o ejecutando `run.bat`.
2. Ingrese el usuario `admin` y la contraseña `Admin@2026!`.
3. Una vez en el Dashboard, presione el botón **"CARGAR ARCHIVOS DEMO"** para poblar el sistema con datos de ejemplo realistas. Esto cargará una lista de 5 ventas y una planilla de movimientos bancarios del Banco Familiar.

### Paso 2.2: Configuración de Reglas de Conciliación
En el panel izquierdo del Dashboard, configure las reglas que regirán el motor de matching:
- **Tolerancia de Fecha (Días):** Define la diferencia máxima admisible de días entre la venta y el movimiento del banco (por ejemplo, 3 días).
- **Tolerancia de Monto:** Define la diferencia de importe máxima admisible (generalmente `0.0` para matching exacto o un valor marginal de redondeo).

### Paso 2.3: Importación de Archivos Reales
Si desea procesar sus propios datos financieros en lugar de los demos:
- Presione **"Importar Ventas"** para seleccionar una planilla CSV de ventas locales o un XML de SIFEN/DTE (Factura Electrónica de Paraguay).
- Presione **"Importar Banco"** para abrir el selector de formatos. Elija el preset correspondiente (Banco Familiar, Banco Continental, Banco Itaú, Banco Basa, MT940, o CAMT.053 XML) y seleccione su extracto.

### Paso 2.4: Ejecución de la Conciliación Criptográfica
1. Una vez cargadas ambas planillas, presione el botón **"CONCILIAR Y GUARDAR"**.
2. El motor de emparejamiento comparará cada registro. Los estados resultantes serán:
   - **CONCILIADA (Verde):** Match perfecto de referencia/cliente, fecha y monto dentro de los límites de tolerancia.
   - **DISCREPANCIA (Amarillo):** La referencia coincide, pero excede los rangos de tolerancia de fecha o monto.
   - **PENDIENTE (Gris):** No se encontró ningún movimiento correlativo ni por referencia ni por nombre de cliente.
3. El sistema generará automáticamente un hash SHA-256 por cada fila (`row_hash`) y un bloque criptográfico local (`block_hash`) en el ledger inmutable, encadenado al bloque anterior.

---

## 3. Funciones Especiales y Módulos Adicionales

### Pestaña "Cotización"
Permite consultar en tiempo real las tasas de arbitraje de divisas USD/PYG provistas por el Banco Central del Paraguay (BCP), la SET y bancos de plaza paraguayos.
- Presione **"Actualizar Cotizaciones Online"** para consumir la API pública de `dolar.melizeche.com`.
- Si se encuentra sin conexión, la app cargará los últimos datos guardados de forma segura en la base de datos SQLite.
- Utilice el conversor integrado para arbitrar montos de USD a PYG o viceversa con la cotización de la fuente que prefiera.

### Pestaña "Historial de Corridas"
Permite auditar el histórico de conciliaciones ejecutadas. Cada corrida tiene un código único formateado como `CONC-YYYYMMDD-HHMMSS`.
- Seleccione cualquier fila del historial y haga clic en **"Cargar Corrida Seleccionada"** para re-visualizar todos los detalles del matching en su pantalla principal.

### Pestaña "Auditoría"
Registra cada evento crítico del sistema (login, login fallido, importaciones, conciliación, cambios de usuario, restauración de copias de seguridad).
- Los registros de auditoría están encadenados de extremo a extremo mediante hashes criptográficos (`prev_hash` + `event_hash`).
- Presione **"Verificar Integridad de Bitácora"** para verificar que ningún registro del sistema haya sido eliminado o manipulado externamente.

### Pestaña "Copias de Seguridad Cifradas" (Admin)
Permite resguardar la base de datos de manera robusta y segura:
- Ingrese una contraseña de respaldo y haga clic en **"Crear Respaldo Cifrado"** para generar un archivo seguro `.cplybak`.
- La restauración de un respaldo valida la firma digital de integridad (HMAC-SHA256) antes de desencriptar para evitar inyecciones de datos alterados.

### Pestaña "Sincronización LAN" (Admin)
Permite habilitar un servidor HTTP embebido local para exportar e importar instantáneas financieras entre terminales de la red local sin internet:
- Presione **"Iniciar Servidor LAN"** para habilitar el endpoint `/snapshot`.
- Desde otra terminal en la red, ingrese la URL del snapshot y presione **"Sincronizar"** para importar nuevas corridas sin sobrescribir los datos locales.
