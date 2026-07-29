# ConciliaPyme Ledger Pro - v2.3.0

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**ConciliaPyme Ledger Pro** es una aplicación comercial de escritorio diseñada para automatizar la conciliación financiera de Pequeñas y Medianas Empresas (PYMES) de la República del Paraguay. Combina un potente motor de emparejamiento con el almacenamiento inmutable de evidencias en un ledger criptográfico local tipo blockchain de bloques enlazados, preparado para integrarse con soluciones distribuidas basadas en **Hyperledger Fabric**.

Desarrollada basándose en la tesis *"Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permissionada"*, la app permite importar comprobantes de ventas, extractos de bancos, conciliar de forma inteligente, registrar eventos de auditoría inalterables, consultar cotizaciones de arbitraje online y exportar reportes integrales.

---

## 🚀 Características Principales

1. **Autenticación Segura (Auth):**
   - PBKDF2-SHA256 con sal única.
   - Bloqueo de cuenta tras 5 intentos fallidos por un periodo temporal de 15 minutos.
   - Roles definidos: `admin`, `contador`, `gerente`, `auditor`.
   - Política de contraseña fuerte (min 10 caracteres, mayúscula, minúscula, número, símbolo).

2. **Dashboard y Motor de Conciliación:**
   - Métricas en tiempo real: procesados, conciliadas, discrepancias, pendientes, bloques de ledger.
   - Reglas configurables de tolerancia por días y diferencia de montos.
   - Generación de resultados en tres estados: `conciliada`, `discrepancia` y `pendiente`.
   - Generación de bloque criptográfico enlazado (`block_hash`) por corrida en SQLite local.
   - Verificación de la integridad matemática del ledger local.

3. **Importadores Soportados:**
   - Planilla CSV de ventas.
   - SIFEN/DTE XML (Factura Electrónica de Paraguay).
   - Planilla CSV de extractos bancarios con presets de bancos locales: *Banco Familiar*, *Banco Continental*, *Banco Itaú* y *Banco Basa*.
   - MT940.
   - CAMT.053 XML (ISO 20022).
   - Generador automático de archivos demo realistas para pruebas.

4. **Arbitraje y Cotizaciones Online:**
   - Consumo de API en tiempo real (`dolar.melizeche.com/api/1.0/`).
   - Muestra fuentes de plaza (BCP, SET, familiar, cambioschaco, etc.).
   - Conversor bidireccional USD/PYG.
   - Caché local persistente en SQLite en caso de caída o falta de conexión a internet.

5. **Copias de Seguridad (Backups Cifrados):**
   - Copias cifradas mediante un esquema robusto de Authenticated Encryption (Encrypt-then-MAC con HMAC-SHA256).
   - Protección contra alteración de datos durante el resguardo.
   - Restauración segura con contraseña y validación de integridad previa.

6. **Sincronización LAN:**
   - Servidor HTTP embebido en hilo de fondo para exportar instantáneas transaccionales (`/snapshot`).
   - Importador seguro desde terminales remotas sin sobrescribir información local histórica.

7. **Soporte de Temas Visuales:**
   - Selector en tiempo real de temas: Sistema, Claro o Oscuro.
   - El modo "Sistema" detecta la preferencia nativa del registro de Windows.
   - Tema oscuro futurista e inmersivo con acentos cian/verde.

8. **Hyperledger Fabric Readiness:**
   - Chaincode completo escrito en Go listo para desplegar en redes de consorcio permissionadas.
   - Exportador integrado de payload transaccional JSON listo para invocar el chaincode.

---

## 📂 Estructura del Repositorio

```text
├── src/
│   ├── main.py             # Punto de entrada de la aplicacion
│   ├── ui.py               # Logica de interfaz grafica Tkinter y estilos
│   ├── database.py         # Creacion y sembrado de la base de datos SQLite
│   ├── auth.py             # Control de accesos, políticas de contraseñas y lockout
│   ├── license_module.py   # Validacion de licenciamiento local por RUC y HMAC
│   ├── audit.py            # Log de eventos de auditoria encadenados criptográficamente
│   ├── importers.py        # Modulo de parsers de archivos bancarios y tributarios
│   ├── reconciliation.py   # Motor de conciliacion y generador de bloques de ledger
│   ├── api_quote.py        # Consumo de API de cotizaciones y cache
│   ├── backup.py           # Esquema de cifrado simetrico para copias de seguridad
│   └── sync_server.py      # Servidor HTTP LAN de instantaneas y cliente de importacion
├── tests/                  # Pruebas unitarias de cobertura completa
├── docs/                   # Documentacion tecnica y de usuario
│   ├── MANUAL_USUARIO.md
│   ├── manual_usuario_con_capturas.html
│   └── MEJORAS_COMERCIALES.md
├── fabric/                 # Chaincode en Go para Hyperledger Fabric
│   ├── evidence_contract.go
│   ├── collections_config.json
│   └── README_FABRIC.md
├── installer/              # Guia de firma y empaquetado para Windows
│   ├── sign_app.ps1
│   └── README_INSTALADOR_FIRMADO.md
├── build.bat               # Automatiza la compilacion de PyInstaller en Windows
├── run.bat                 # Lanza la aplicacion de escritorio
└── ConciliaPymeLedgerPro.spec # Archivo de especificacion de PyInstaller
```

---

## 🔧 Instrucciones de Instalación y Ejecución

### Prerrequisitos
- Python 3.10 o superior instalado.

### Clonar y preparar dependencias:
1. Instale las librerías necesarias:
   ```bash
   pip install pytest
   ```
2. Para lanzar la aplicación de escritorio en modo local, ejecute:
   ```bash
   python src/main.py
   ```
   *(En Windows puede usar directamente el archivo `run.bat` haciendo doble clic).*

### Ejecutar Pruebas Automatizadas
Para ejecutar la suite completa de pruebas unitarias y de integración, ejecute:
```bash
PYTHONPATH=. pytest
```

---

## 🛠️ Compilación y Firma en Windows

Consulte las guías completas en `installer/README_INSTALADOR_FIRMADO.md` para empaquetar la aplicación en un archivo ejecutable `.exe` portable firmado con un certificado local de Authenticode:
1. **Compilar:** Ejecute `build.bat` para compilar el ejecutable.
2. **Firmar:** Ejecute `installer/sign_app.ps1` desde una terminal de PowerShell con privilegios de administrador.
3. **Instalador:** Utilice el asistente de Windows `IExpress` para generar un SFX unificado.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para obtener más detalles.

---

*2026 © Creado por Pedro Narváez y Ariel Torres.*
*Desarrollo operativo y robusto para la modernización contable de las PYMES paraguayas mediante tecnología blockchain.*
