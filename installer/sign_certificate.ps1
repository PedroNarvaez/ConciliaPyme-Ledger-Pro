# Script PowerShell para firma de código Authenticode con certificado demo
# ConciliaPyme Ledger Pro
# Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.

param(
    [string]$ExePath = "ConciliaPymeLedgerPro.exe",
    [string]$CertPath = "conciliapyme_cert.pfx",
    [string]$Password = "Demo@2026!"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Firma de Código Authenticode" -ForegroundColor Cyan
Write-Host "  ConciliaPyme Ledger Pro v2.3.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si el archivo existe
if (-not (Test-Path $ExePath)) {
    Write-Host "ERROR: No se encontró $ExePath" -ForegroundColor Red
    exit 1
}

# Crear certificado autofirmado si no existe
if (-not (Test-Path $CertPath)) {
    Write-Host "Creando certificado autofirmado..." -ForegroundColor Yellow
    
    # Crear certificado en el store personal
    $cert = New-SelfSignedCertificate `
        -Type Custom `
        -Subject "CN=ConciliaPyme, O=Pedro Narváez y Ariel Torres, C=PY" `
        -KeyUsage DigitalSignature `
        -KeyLength 2048 `
        -FriendlyName "ConciliaPyme Code Signing" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
    
    Write-Host "Certificado creado: $($cert.Thumbprint)" -ForegroundColor Green
    
    # Exportar a PFX
    $securePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $CertPath -Password $securePassword | Out-Null
    
    Write-Host "Certificado exportado a $CertPath" -ForegroundColor Green
}

# Firmar el ejecutable
Write-Host "Firmando $ExePath..." -ForegroundColor Yellow

try {
    $securePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText
    $pfx = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($CertPath, $securePassword)
    
    Set-AuthenticodeSignature `
        -FilePath $ExePath `
        -Certificate $pfx `
        -TimestampServer "http://timestamp.digicert.com"
    
    Write-Host "¡Ejecutable firmado exitosamente!" -ForegroundColor Green
    
    # Verificar firma
    $signature = Get-AuthenticodeSignature -FilePath $ExePath
    if ($signature.Status -eq "Valid") {
        Write-Host "Firma verificada: $($signature.SignerCertificate.Subject)" -ForegroundColor Green
    } else {
        Write-Host "ADVERTENCIA: Estado de firma: $($signature.Status)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "ERROR al firmar: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "NOTA IMPORTANTE:" -ForegroundColor Yellow
Write-Host "Este certificado es solo para desarrollo/demo." -ForegroundColor Yellow
Write-Host "Para distribución comercial, compre un certificado de CA confiable." -ForegroundColor Yellow
Write-Host "(DigiCert, Sectigo, GlobalSign, etc.)" -ForegroundColor Yellow
