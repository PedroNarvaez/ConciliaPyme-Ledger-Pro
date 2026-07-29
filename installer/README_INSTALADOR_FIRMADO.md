# Instalador y Firma de Código - ConciliaPyme Ledger Pro

## Descripción

Este documento describe el proceso para generar un ejecutable firmado de ConciliaPyme Ledger Pro.

## Requisitos Previos

### Para Compilar EXE
- Windows 10/11
- Python 3.8 o superior
- PyInstaller (`pip install pyinstaller`)

### Para Firmar el Código
- PowerShell 5.1 o superior (Windows)
- Certificado de firma de código (demo o comercial)

## Pasos de Construcción

### 1. Generar Ejecutable

```bash
python build_exe.py
```

Esto creará:
- `dist/ConciliaPymeLedgerPro/ConciliaPymeLedgerPro.exe`

### 2. Firmar el Ejecutable (Opcional pero Recomendado)

```powershell
cd installer
.\sign_certificate.ps1 -ExePath "..\dist\ConciliaPymeLedgerPro\ConciliaPymeLedgerPro.exe"
```

Parámetros opcionales:
- `-CertPath`: Ruta al certificado PFX (default: conciliapyme_cert.pfx)
- `-Password`: Contraseña del certificado (default: Demo@2026!)

## Tipos de Certificados

### Certificado Autofirmado (Demo)
- **Ventajas**: Gratis, rápido de obtener
- **Desventajas**: Los usuarios verán advertencia de seguridad
- **Uso**: Desarrollo, testing, distribución interna

### Certificado Comercial
- **Proveedores**: DigiCert, Sectigo, GlobalSign, Entrust
- **Costo**: $200-$500 USD/año
- **Ventajas**: Sin advertencias, mayor confianza
- **Requisitos**: Verificación de identidad de la empresa

## Creación de Instalador con IExpress

Windows incluye IExpress para crear instaladores autoextraíbles:

1. Ejecutar `iexpress.exe` desde Inicio
2. Seleccionar "Create new Self Extraction Directive file"
3. Elegir "Extract files and run an installation command"
4. Agregar archivos:
   - ConciliaPymeLedgerPro.exe
   - Archivos de datos necesarios
5. Configurar comando de instalación: `ConciliaPymeLedgerPro.exe`
6. Guardar como `.sed` y generar `.exe`

## Alternativa: Inno Setup

Para instaladores más profesionales:

```pascal
[Setup]
AppName=ConciliaPyme Ledger Pro
AppVersion=2.3.0
DefaultDirName={pf}\ConciliaPyme
DefaultGroupName=ConciliaPyme
OutputBaseFilename=ConciliaPymeLedgerPro_Setup

[Files]
Source: "dist\ConciliaPymeLedgerPro\*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "data\*"; DestDir: "{app}\data"

[Icons]
Name: "{group}\ConciliaPyme Ledger Pro"; Filename: "{app}\ConciliaPymeLedgerPro.exe"
```

## Verificación de Firma

Para verificar que un ejecutable está firmado:

```powershell
Get-AuthenticodeSignature -FilePath "ConciliaPymeLedgerPro.exe"
```

Resultado esperado:
```
SignerCertificate      Status
-----------------      ------
CN=ConciliaPyme...     Valid
```

## Troubleshooting

### Error: "The signer's name is not valid"
El certificado autofirmado no es reconocido. Use certificado comercial para distribución.

### Error: "File is already signed"
Remueva la firma existente antes de volver a firmar:
```powershell
Remove-Signature -FilePath "archivo.exe"
```

### Advertencia SmartScreen
Es normal para certificados nuevos. Mejora con el tiempo y uso.

## Notas de Seguridad

1. **Nunca comparta su certificado comercial** - Es equivalente a su firma legal
2. **Use timestamping** - Mantiene la firma válida después de expiración
3. **Renueve antes de expirar** - Evite interrupciones en distribución

---

Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.
