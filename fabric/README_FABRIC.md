# Integración con Hyperledger Fabric - ConciliaPyme Ledger Pro

Este directorio contiene el chaincode oficial (contrato inteligente) escrito en Go para el registro y validación de evidencias criptográficas generadas por ConciliaPyme Ledger Pro en una red blockchain permissionada.

## Estructura del Chaincode
El chaincode expone las siguientes funciones:
- `RegisterEvidence`: Registra el ID de evidencia, hashes transaccionales, hashes del bloque local, timestamp y metadatos del actor tras verificar que la firma coincida.
- `ReadEvidence`: Recupera un registro de evidencia por ID desde el estado mundial.
- `EvidenceExists`: Comprueba si ya existe una evidencia específica.
- `VerifyEvidence`: Recalcula el hash SHA-256 de los atributos almacenados y lo compara con el blockHash guardado para garantizar que no haya habido alteración alguna en el ledger distribuido.
- `ComputeHash`: Función auxiliar que recalcula la firma concatenando los atributos de bloque usando el delimitador `|`.

---

## Instrucciones de Despliegue en `fabric-samples/test-network`

Para desplegar este chaincode en la red de pruebas de Hyperledger Fabric (`test-network`), siga los pasos detallados a continuación:

### Paso 1: Prerrequisitos
Asegúrese de tener instalados:
- Docker y Docker Compose.
- Go (v1.20 o superior).
- Binarios de Hyperledger Fabric (v2.4 o v2.5) y `fabric-samples`.

### Paso 2: Copiar el Chaincode al Directorio de Pruebas
Copie este directorio `fabric/` dentro de la carpeta de chaincodes de sus muestras de Fabric:
```bash
cp -r fabric/ path/to/fabric-samples/chaincode/fabric-evidence
```

### Paso 3: Levantar la Red de Pruebas
Navegue al directorio de `test-network` y levante la red con un canal (por ejemplo, `mychannel`):
```bash
cd path/to/fabric-samples/test-network
./network.sh up createChannel -c mychannel -ca
```

### Paso 4: Desplegar el Chaincode con Colección Privada (Private Data)
Para habilitar colecciones privadas, use el archivo `collections_config.json` provisto. Despliegue el chaincode en Go especificando el canal y la configuración de colecciones:
```bash
./network.sh deployCC \
  -c mychannel \
  -ccn fabric-evidence \
  -ccp ../chaincode/fabric-evidence \
  -ccl go \
  -cccg ../chaincode/fabric-evidence/collections_config.json
```

### Paso 5: Invocar y Consultar desde la Línea de Comandos (CLI)

#### Registrar una evidencia de prueba (Invocación):
```bash
peer chaincode invoke \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls \
  --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlscacerts-example-com-cert.pem \
  -C mychannel \
  -n fabric-evidence \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
  --peerAddresses localhost:9051 \
  --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
  -c '{"function":"RegisterEvidence","Args":["EVID-1","2026-03-01T12:00:00","admin","NODE-PY-01","Hyperledger Fabric (Permissioned)","tx_hash_123","prev_hash_abc","computed_block_hash_xyz","COMMITTED"]}'
```

#### Consultar una evidencia registrada:
```bash
peer chaincode query -C mychannel -n fabric-evidence -c '{"Args":["ReadEvidence","EVID-1"]}'
```

#### Verificar integridad de una evidencia:
```bash
peer chaincode query -C mychannel -n fabric-evidence -c '{"Args":["VerifyEvidence","EVID-1"]}'
```
