# ConciliaPyme Ledger Pro

## Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permisionada

**Versión:** 2.3.0  
**Copyright:** 2026 © Creado por Pedro Narváez y Ariel Torres.

---

## 📋 Descripción

ConciliaPyme Ledger Pro es una aplicación de escritorio para Windows que permite a las PYMES paraguayas:

- Importar ventas y movimientos bancarios desde múltiples formatos
- Conciliar automáticamente transacciones
- Generar evidencia criptográfica tipo blockchain
- Administrar usuarios con roles y permisos
- Exportar reportes en JSON y CSV
- Consultar cotización USD/PYG en tiempo real
- Preparar integración con Hyperledger Fabric

---

## 🚀 Características Principales

### Seguridad
- ✅ Login con bloqueo tras 5 intentos fallidos
- ✅ Contraseñas hasheadas con PBKDF2-SHA256
- ✅ Auditoría con hash encadenado
- ✅ Backup cifrado con extensión `.cplybak`

### Conciliación
- ✅ Algoritmo inteligente de matching
- ✅ Estados: conciliada, discrepancia, pendiente
- ✅ Ledger blockchain local verificable
- ✅ Códigos únicos por corrida (CONC-YYYYMMDD-HHMMSS)

### Formatos Soportados
| Formato | Tipo | Extensión |
|---------|------|-----------|
| CSV Ventas | Planilla | .csv |
| CSV Banco | Extracto | .csv |
| MT940 | Banking | .txt |
| CAMT.053 | XML SEPA | .xml |
| SIFEN/DTE | Facturación PY | .xml |

### Cotización USD/PYG
- API en tiempo real: https://dolar.melizeche.com/api/1.0/
- Fuentes: BCP, SET, Familiar, Cambios Chaco
- Caché local si no hay conexión
- Conversor integrado

---

## 📦 Instalación

### Requisitos
- Windows 10/11
- Python 3.8+
- 4 GB RAM mínimo

### Ejecución Rápida

```bash
# Doble click en:
run_app.bat

# O desde consola:
python src\conciliapyme.py
```

### Credenciales por Defecto
```
Usuario: admin
Contraseña: Admin@2026!
```

---

## 🏗️ Estructura del Proyecto

```
/workspace
├── src/
│   └── conciliapyme.py        # Aplicación principal
├── data/                       # Base de datos SQLite (auto-generado)
├── demo/                       # Archivos de ejemplo (auto-generado)
├── fabric/
│   ├── chaincode.go           # Chaincode Hyperledger
│   ├── collections_config.json # Private data config
│   └── README_FABRIC.md       # Documentación Fabric
├── docs/
│   ├── MANUAL_USUARIO.md      # Manual completo
│   └── MEJORAS_COMERCIALES.md # Roadmap futuro
├── installer/
│   ├── sign_certificate.ps1   # Script firma Authenticode
│   └── README_INSTALADOR_FIRMADO.md
├── build_exe.py               # Generador de EXE
├── run_app.bat                # Launcher Windows
└── README.md                  # Este archivo
```

---

## 🎯 Uso Básico

### 1. Cargar Datos Demo
```
Dashboard → "Cargar Datos Demo"
```

### 2. Importar Archivos
```
Pestaña "Importar Datos" → Seleccionar tipo → Importar
```

### 3. Ejecutar Conciliación
```
Pestaña "Conciliación" → Ejecutar → Guardar Resultados
```

### 4. Verificar Ledger
```
Dashboard → "Verificar Ledger"
```

### 5. Exportar Reportes
```
Dashboard → "Exportar JSON" o "Exportar CSV"
```

---

## 🔧 Desarrollo

### Compilar Ejecutable

```bash
pip install pyinstaller
python build_exe.py
```

El EXE se generará en `dist/ConciliaPymeLedgerPro/`

### Firmar Código (Windows)

```powershell
cd installer
.\sign_certificate.ps1 -ExePath "..\dist\ConciliaPymeLedgerPro\ConciliaPymeLedgerPro.exe"
```

---

## 📚 Documentación Adicional

- [Manual de Usuario](docs/MANUAL_USUARIO.md)
- [Integración Hyperledger Fabric](fabric/README_FABRIC.md)
- [Instalador y Firma](installer/README_INSTALADOR_FIRMADO.md)
- [Mejoras Comerciales Futuras](docs/MEJORAS_COMERCIALES.md)

---

## 🔐 Consideraciones de Seguridad

1. **Cambie la contraseña admin por defecto** inmediatamente
2. **Realice backups periódicos** cifrados
3. **Guarde las claves de backup** en lugar seguro
4. Para producción, use **certificado comercial** para firmar el EXE

---

## 🤝 Soporte

Para asistencia técnica o consultas comerciales:

- Email: soporte@conciliapyme.com.py
- Documentación: `/docs`

---

## 📄 Licencia

Software propietario. Todos los derechos reservados.

- Uso personal y comercial permitido con licencia válida
- Prohibida la ingeniería inversa
- Prohibida la redistribución sin autorización

---

## 👨‍💻 Autores

**Pedro Narváez y Ariel Torres**

Basado en tesis: *"Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permissionada"*

---

## 🙏 Agradecimientos

- Banco Central del Paraguay (datos de cotización)
- Hyperledger Project (blockchain permissionada)
- Comunidad Python Paraguay

---

*Última actualización: Enero 2026*
