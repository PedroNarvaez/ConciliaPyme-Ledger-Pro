# ConciliaPyme Ledger Pro - Web Edition

## Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permisionada

**Versión:** 3.0.0 Web  
**Copyright:** 2026 © Creado por Pedro Narváez y Ariel Torres.

---

## 📋 Descripción

ConciliaPyme Ledger Pro es una **aplicación web moderna** desarrollada con React + TypeScript + Vite que permite a las PYMES paraguayas:

- Importar ventas y movimientos bancarios desde múltiples formatos (CSV, MT940, CAMT.053, XML SIFEN/DTE)
- Conciliar automáticamente transacciones con algoritmo inteligente de matching
- Generar evidencia criptográfica tipo blockchain con hash SHA-256 encadenado
- Administrar usuarios multi-compañía con roles y permisos granulares
- Visualizar datos bancarios CAMT.053 con árbol XML interactivo
- Generar informes ejecutivos y técnicos exportables a PDF/CSV
- Realizar auditorías completas con trazabilidad de operaciones
- Consultar cotización USD/PYG en tiempo real
- Modo oscuro/claro adaptable
- Preparado para integración con Hyperledger Fabric

---

## 🚀 Características Principales

### Seguridad Avanzada
- ✅ Login seguro con validación de credenciales
- ✅ Gestión multi-usuario y multi-empresa
- ✅ Auditoría con hash encadenado verificable
- ✅ Certificados digitales con timestamp y hash SHA-256
- ✅ Roles: Administrador, Contador, Auditor, Operador

### Conciliación Inteligente
- ✅ Algoritmo de matching por monto, fecha y referencia
- ✅ Estados: conciliada, discrepancia, pendiente, revisada
- ✅ Ledger blockchain local inmutable
- ✅ Códigos únicos por corrida (CONC-YYYYMMDD-HHMMSS)
- ✅ Auto-conciliación con umbrales configurables

### Visor CAMT.053 ISO 20022
- ✅ Parseo de XML CAMT.053
- ✅ Validación de estructura ISO 20022
- ✅ Árbol XML interactivo colapsable
- ✅ Extracción de datos estructurados
- ✅ Detección de errores de formato

### Módulos Incluidos
| Módulo | Funcionalidad | Estado |
|--------|--------------|--------|
| Login | Autenticación multi-usuario | ✅ Activo |
| Dashboard | Vista general de métricas | ✅ Activo |
| Visor CAMT | Visualizador XML CAMT.053 | ✅ Activo |
| Informe | Generador de reportes | ✅ Activo |
| Conciliación | Motor de matching automático | ✅ Activo |
| Auditoría | Trazabilidad completa | ✅ Activo |

### Formatos Soportados
| Formato | Tipo | Extensión |
|---------|------|-----------|
| CSV Ventas | Planilla comercial | .csv |
| CSV Banco | Extracto bancario | .csv |
| MT940 | Banking internacional | .txt |
| CAMT.053 | XML SEPA ISO 20022 | .xml |
| SIFEN/DTE | Facturación electrónica PY | .xml |

### Cotización USD/PYG
- API en tiempo real: https://dolar.melizeche.com/api/1.0/
- Fuentes: BCP, SET, Familiar, Cambios Chaco
- Caché local si no hay conexión
- Conversor integrado en tiempo real

### Exportación
- 📄 PDF con formato profesional
- 📊 CSV compatible con Excel/Google Sheets
- 🔐 Certificados JSON con hash criptográfico

---

## 📦 Instalación y Uso

### Requisitos Previos
- Node.js 18+ instalado
- Navegador web moderno (Chrome, Firefox, Edge)
- Conexión a internet (para APIs externas)

### Instalación Rápida

```bash
# 1. Instalar dependencias
npm install

# 2. Iniciar servidor de desarrollo
npm run dev

# 3. Abrir navegador en http://localhost:5173
```

### Credenciales por Defecto

**Usuario Administrador:**
```
Usuario: admin
Contraseña: Admin@2026!
```

**Usuarios Demo Incluidos:**
| Usuario | Rol | Contraseña |
|---------|-----|------------|
| admin | Administrador | Admin@2026! |
| contador | Contador | Contador@2026! |
| auditor | Auditor | Auditor@2026! |
| operador | Operador | Operador@2026! |

---

## 🏗️ Estructura del Proyecto

```
/workspace
├── src/
│   ├── main.tsx              # Punto de entrada React
│   ├── index.css             # Estilos globales Tailwind
│   └── conciliapyme.py       # Versión legacy Python (referencia)
├── public/                    # Assets estáticos
├── docs/
│   ├── MANUAL_USUARIO.md     # Manual completo
│   └── MEJORAS_COMERCIALES.md # Roadmap futuro
├── fabric/
│   ├── chaincode.go          # Chaincode Hyperledger
│   ├── collections_config.json # Private data config
│   └── README_FABRIC.md      # Documentación Fabric
├── installer/
│   └── ...                   # Scripts de firma (legacy)
├── index.html                # HTML principal
├── package.json              # Dependencias npm
├── tsconfig.json             # Configuración TypeScript
├── vite.config.ts            # Configuración Vite
├── tailwind.config.js        # Configuración Tailwind CSS
└── README.md                 # Este archivo
```

---

## 🎯 Uso Básico

### 1. Inicio de Sesión
```
→ Ingresar usuario y contraseña
→ Seleccionar empresa (si tiene múltiples)
→ Click en "Iniciar Sesión"
```

### 2. Dashboard Principal
```
→ Vista general de métricas financieras
→ Accesos rápidos a módulos
→ Estado de conciliaciones pendientes
→ Cotización USD/PYG en tiempo real
```

### 3. Visor CAMT.053
```
→ Módulo "Visor CAMT"
→ Cargar archivo XML .camt.053
→ Validar estructura ISO 20022
→ Explorar árbol XML interactivo
→ Extraer datos estructurados
```

### 4. Conciliación Automática
```
→ Módulo "Conciliación"
→ Cargar ventas (CSV) y extracto bancario (CSV/CAMT)
→ Configurar umbrales de matching
→ Ejecutar auto-conciliación
→ Revisar resultados y ajustar manualmente si es necesario
→ Guardar corrida con código único
```

### 5. Generar Informes
```
→ Módulo "Informe"
→ Seleccionar tipo de reporte (Ejecutivo/Técnico)
→ Filtrar por fechas y estados
→ Exportar a PDF o CSV
→ Generar certificado con hash
```

### 6. Auditoría
```
→ Módulo "Auditoría"
→ Ver historial completo de operaciones
→ Trazabilidad de cambios
→ Verificar integridad del ledger
→ Exportar logs de auditoría
```

---

## 🔧 Desarrollo y Build

### Servidor de Desarrollo

```bash
npm run dev
```
Abre la aplicación en modo desarrollo con hot-reload en http://localhost:5173

### Build de Producción

```bash
npm run build
```
Genera archivos optimizados en la carpeta `dist/`

### Preview de Producción

```bash
npm run preview
```
Sirve la aplicación desde `dist/` localmente

### Linting y Type Checking

```bash
npm run lint
npm run type-check
```

---

## 🌐 Despliegue

### Opción 1: Hosting Estático (Recomendado)

La aplicación compilada (`dist/`) puede desplegarse en:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Google Cloud Storage
- Azure Static Web Apps

### Opción 2: Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist
EXPOSE 80
CMD ["npx", "serve", "-s", "dist"]
```

### Opción 3: Servidor Web Tradicional

Copiar el contenido de `dist/` a cualquier servidor web:
- Apache
- Nginx
- IIS

Configurar rewrite rules para SPA (Single Page Application).

---

## 🔐 Consideraciones de Seguridad

1. **Cambie las contraseñas por defecto** inmediatamente después de instalar
2. **Use HTTPS** en producción (obligatorio para credenciales)
3. **Implemente autenticación real** (JWT, OAuth2, SAML) para producción
4. **Habilite CORS** solo para dominios autorizados
5. **Realice backups periódicos** de la configuración y datos
6. **Revise los logs de auditoría** regularmente
7. **Mantenga actualizadas** las dependencias de npm

> ⚠️ **Nota:** Esta versión web incluye autenticación simulada para demostración. Para uso en producción, debe integrarse con un backend seguro que gestione sesiones, tokens JWT y almacenamiento persistente.

---

## 📚 Documentación Adicional

- [Manual de Usuario Completo](docs/MANUAL_USUARIO.md)
- [Integración Hyperledger Fabric](fabric/README_FABRIC.md)
- [Mejoras Comerciales Futuras](docs/MEJORAS_COMERCIALES.md)
- [Guía de Formatos Bancarios](docs/formatos_bancarios.md) (próximamente)

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| React | 19.x | Framework UI |
| TypeScript | 5.x | Tipado estático |
| Vite | 6.x | Build tool y dev server |
| Tailwind CSS | 3.x | Estilos utilitarios |
| Lucide React | latest | Iconos modernos |
| jspdf | latest | Generación de PDF |
| Crypto API | Native | Hash SHA-256 |

---

## 🤝 Soporte

Para asistencia técnica o consultas comerciales:

- Email: soporte@conciliapyme.com.py
- Documentación: `/docs`
- Issues: GitHub Repository

---

## 📄 Licencia

Software propietario. Todos los derechos reservados.

- Uso personal y comercial permitido con licencia válida
- Prohibida la ingeniería inversa
- Prohibida la redistribución sin autorización
- El código fuente demo es solo para evaluación

---

## 👨‍💻 Autores

**Pedro Narváez y Ariel Torres**

Basado en tesis: *"Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permissionada"*

---

## 🙏 Agradecimientos

- Banco Central del Paraguay (datos de cotización)
- Hyperledger Project (blockchain permissionada)
- Comunidad Python Paraguay
- Comunidad React Latinoamérica

---

## 📈 Roadmap

- [ ] Backend Node.js/Express con autenticación JWT
- [ ] Base de datos PostgreSQL/MongoDB
- [ ] Integración real con Hyperledger Fabric
- [ ] API REST documentada con Swagger
- [ ] Notificaciones email/SMS
- [ ] Multi-idioma (Español/Inglés/Guaraní)
- [ ] App móvil React Native
- [ ] Machine Learning para predicción de discrepancias

---

*Última actualización: Enero 2026 - Versión Web 3.0.0*
