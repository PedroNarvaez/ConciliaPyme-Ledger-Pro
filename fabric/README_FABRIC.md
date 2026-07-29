# Integración con Hyperledger Fabric

## Descripción

Este módulo contiene el chaincode de Go para Hyperledger Fabric, que permite registrar y verificar evidencias de conciliación financiera en una blockchain permissionada.

## Requisitos

- Docker y Docker Compose
- Hyperledger Fabric samples (fabric-samples)
- Go 1.18 o superior
- Node.js 16+ (opcional, para aplicaciones cliente)

## Estructura de Archivos

```
fabric/
├── chaincode.go              # Chaincode principal
├── collections_config.json   # Configuración de private data collection
└── README_FABRIC.md          # Este archivo
```

## Funciones del Chaincode

### RegisterEvidence
Registra una nueva evidencia de conciliación en el ledger.

**Parámetros:**
- `evidenceJSON`: JSON con los datos de la evidencia

**Ejemplo:**
```bash
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com \
  --tls --cafile ${CA_FILE} -C mychannel -n conciliapyme \
  --peerAddresses localhost:7051 --peerAddresses localhost:9051 \
  --tlsRootCertFiles ${TLS_CERT_1} --tlsRootCertFiles ${TLS_CERT_2} \
  -c '{"function":"RegisterEvidence","args":["{\"saleRef\":\"VNT-001\",\"bankRef\":\"REF-001\",\"status\":\"conciliada\",\"saleAmount\":1500000,\"bankAmount\":1500000}"]}'
```

### ReadEvidence
Lee una evidencia existente por su clave.

**Parámetros:**
- `evidenceKey`: Clave única de la evidencia

**Ejemplo:**
```bash
peer chaincode query -C mychannel -n conciliapyme \
  -c '{"function":"ReadEvidence","args":["EVIDENCE-0-VNT-001"]}'
```

### EvidenceExists
Verifica si existe una evidencia.

**Ejemplo:**
```bash
peer chaincode query -C mychannel -n conciliapyme \
  -c '{"function":"EvidenceExists","args":["EVIDENCE-0-VNT-001"]}'
```

### VerifyEvidence
Verifica la integridad criptográfica de una evidencia.

**Ejemplo:**
```bash
peer chaincode query -C mychannel -n conciliapyme \
  -c '{"function":"VerifyEvidence","args":["EVIDENCE-0-VNT-001"]}'
```

### ComputeHash
Calcula hash SHA-256 de datos arbitrarios.

**Ejemplo:**
```bash
peer chaincode query -C mychannel -n conciliapyme \
  -c '{"function":"ComputeHash","args":["datos-a-hashear"]}'
```

## Despliegue en Test Network

### 1. Iniciar Test Network

```bash
cd fabric-samples/test-network
./network.sh down
./network.sh up createChannel -ca
```

### 2. Desplegar Chaincode

```bash
./network.sh deployCC -ccn conciliapyme -ccp ../../workspace/fabric/ \
  -ccl go -ccep "OR('Org1MSP.peer','Org2MSP.peer')" \
  --collections-config ../../workspace/fabric/collections_config.json
```

### 3. Verificar Despliegue

```bash
peer chaincode query -C mychannel -n conciliapyme \
  -c '{"function":"GetLedgerState","args":[]}'
```

## Private Data Collection

El chaincode utiliza un private data collection llamado `conciliapymePrivateData` para almacenar información sensible de manera confidencial entre las organizaciones autorizadas.

La configuración se encuentra en `collections_config.json` e incluye:
- Política de acceso para Org1 y Org2
- Required peer count: 1
- Max peer count: 3
- Block to live: 1000000 (aproximadamente indefinido)

## Aplicación Cliente de Ejemplo

Para integrar la aplicación de escritorio con Fabric:

1. Exportar payload desde la app usando "Exportar Payload Fabric"
2. Usar el SDK de Fabric para enviar la transacción:

```javascript
const { Gateway, Wallets } = require('fabric-network');
const fs = require('fs');
const path = require('path');

async function registerEvidence(evidenceData) {
    const wallet = await Wallets.newFileSystemWallet('./wallet');
    const gateway = new Gateway();
    
    await gateway.connect(ccp, {
        wallet,
        identity: 'appUser',
        discovery: { enabled: true, asLocalhost: true }
    });

    const network = await gateway.getNetwork('mychannel');
    const contract = network.getContract('conciliapyme');
    
    const evidenceJSON = JSON.stringify(evidenceData);
    await contract.submitTransaction('RegisterEvidence', evidenceJSON);
    
    await gateway.disconnect();
}
```

## Comandos Útiles

### Ver logs del chaincode
```bash
docker logs -f dev-peer0.org1.example.com-conciliapyme-1.0
```

### Listar chaincodes instalados
```bash
peer lifecycle chaincode queryinstalled
```

### Consultar estado del ledger
```bash
peer chaincode query -C mychannel -n conciliapyme \
  -c '{"function":"GetLedgerState","args":[]}'
```

## Consideraciones de Seguridad

1. **Certificados**: Para producción, use certificados CA comerciales
2. **Políticas de Endorsement**: Ajuste según requerimientos de negocio
3. **Private Data**: Configure colecciones privadas para datos sensibles
4. **TLS**: Siempre habilitado para comunicaciones

## Troubleshooting

### Error: chaincode not found
Verifique que el chaincode esté instalado y aprobado en el canal.

### Error: endorsement policy failure
Asegúrese de tener suficientes peers para satisfacer la política.

### Error: private data collection not found
Verifique que collections_config.json se haya especificado al desplegar.

---

Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.
