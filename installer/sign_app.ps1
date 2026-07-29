# PowerShell Script for Code Signing - ConciliaPyme Ledger Pro
# Generates a local self-signed Authenticode certificate and signs the built EXE file.
# Note: This is for local testing. In commercial distribution, a certificate from a trusted CA is required.

$exePath = "dist\ConciliaPymeLedgerPro.exe"

if (-not (Test-Path $exePath)) {
    Write-Warning "No se encontro el archivo executable en '$exePath'. Asegurese de ejecutar build.bat primero."
    Exit
}

Write-Host "Generando certificado auto-firmado de prueba para Code Signing..." -ForegroundColor Cyan

# Create self-signed code signing certificate in the user store
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=ConciliaPyme Demo CodeSigning, O=Pedro Narvaez & Ariel Torres, C=PY" -FriendlyName "ConciliaPyme Test Sign"

if ($cert) {
    Write-Host "Certificado creado con exito. Thumbprint: $($cert.Thumbprint)" -ForegroundColor Green

    Write-Host "Firmando digitalmente el archivo ejecutable '$exePath'..." -ForegroundColor Cyan
    # Sign the executable using standard cmdlet
    Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert

    Write-Host "Firma completada con exito." -ForegroundColor Green
} else {
    Write-Error "No se pudo generar el certificado de firma de codigo."
}
