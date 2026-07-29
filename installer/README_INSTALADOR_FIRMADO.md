# Instrucciones de Instalación, Compilación y Firma de Código

Este directorio contiene las herramientas para compilar, empaquetar y firmar el ejecutable de **ConciliaPyme Ledger Pro** en entornos Windows.

---

## 1. Generación del Ejecutable (`.exe`)

Para empaquetar el script de Python junto con el intérprete en un solo archivo ejecutable portable sin dependencias externas, ejecute:

```cmd
build.bat
```

Este script utiliza **PyInstaller** y lee la configuración contenida en `ConciliaPymeLedgerPro.spec` para generar el ejecutable portable en:
`dist\ConciliaPymeLedgerPro.exe`

---

## 2. Firma Digital de Código (Authenticode)

Windows SmartScreen puede bloquear la ejecución de archivos `.exe` no reconocidos o sin firma digital. Para mitigar esto localmente, hemos provisto un script de PowerShell que crea un certificado de firma de código auto-firmado de demostración y lo aplica sobre el ejecutable.

### Pasos para Firmar el Ejecutable Localmente:
1. Abra PowerShell como **Administrador**.
2. Ejecute el script de firma:
   ```powershell
   powershell -ExecutionPolicy Bypass -File installer/sign_app.ps1
   ```
3. El script creará un certificado auto-firmado y firmará el ejecutable `dist\ConciliaPymeLedgerPro.exe` usando la firma digital de Microsoft Authenticode.

> ⚠️ **Advertencia Importante para Venta Comercial Real:**
> Los certificados auto-firmados de demostración solo son confiables en la máquina donde se crearon. Para una venta real a PYMES paraguayas, debe adquirir un certificado comercial de firma de código emitido por una Autoridad de Certificación (CA) públicamente confiable (ej. Sectigo, DigiCert, GlobalSign) y firmar el ejecutable usando `signtool.exe` de Microsoft Windows SDK.

---

## 3. Creación de Instalador Portable (IExpress)

Windows incluye una herramienta nativa llamada **IExpress** que permite crear instaladores auto-extraíbles (`SFX` / EXE portables) de forma sencilla.

### Instrucciones para crear el Instalador Portable con IExpress:
1. Presione `Win + R`, escriba `iexpress` y presione Enter para iniciar el asistente.
2. Seleccione **Create new Self Extraction Directive file** y presione Siguiente.
3. Seleccione **Extract files and run an installation command** y presione Siguiente.
4. Escriba el título de la app: `ConciliaPyme Ledger Pro`.
5. Seleccione **No prompt** y **Do not display a license** (o agregue su archivo de licencia de texto).
6. Agregue el archivo empaquetado: `dist\ConciliaPymeLedgerPro.exe`.
7. En el cuadro **Install Program to Launch**, escriba `ConciliaPymeLedgerPro.exe`. En **Post Install Command**, déjelo en blanco.
8. Seleccione **Hidden** para la ventana de extracción y **No message** al finalizar.
9. Guarde el archivo de salida con el nombre del instalador portable final, por ejemplo: `ConciliaPymeLedgerPro_Installer.exe`.
10. Presione Siguiente para generar el instalador portable unificado.

¡Listo! El instalador portable empaquetará la aplicación y la ejecutará con un solo doble clic de forma segura.
