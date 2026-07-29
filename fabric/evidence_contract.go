package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// EvidenceContract contract for managing financial reconciliation evidence hashes
type EvidenceContract struct {
	contractapi.Contract
}

// Evidence defines the structure of a reconciliation block registered on the ledger
type Evidence struct {
	ID        string `json:"id"`
	Timestamp string `json:"timestamp"`
	Actor     string `json:"actor"`
	Node      string `json:"node"`
	Platform  string `json:"platform"`
	TxHash    string `json:"txHash"`
	PrevHash  string `json:"prevHash"`
	BlockHash string `json:"blockHash"`
	Status    string `json:"status"`
}

// ComputeHash calculates the expected block hash of the evidence
func (c *EvidenceContract) ComputeHash(prevHash, txHash, timestamp, actor, node, platform, status string) string {
	payload := fmt.Sprintf("%s|%s|%s|%s|%s|%s|%s", prevHash, txHash, timestamp, actor, node, platform, status)
	hash := sha256.Sum256([]byte(payload))
	return hex.EncodeToString(hash[:])
}

// RegisterEvidence registers a new reconciliation block as evidence in the ledger state
func (c *EvidenceContract) RegisterEvidence(ctx contractapi.TransactionContextInterface, id string, timestamp string, actor string, node string, platform string, txHash string, prevHash string, blockHash string, status string) error {
	exists, err := c.EvidenceExists(ctx, id)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the evidence %s already exists", id)
	}

	// Verify hash integrity before storing
	computed := c.ComputeHash(prevHash, txHash, timestamp, actor, node, platform, status)
	if computed != blockHash {
		return fmt.Errorf("hash verification failed. Provided blockHash does not match computed hash: %s", computed)
	}

	evidence := Evidence{
		ID:        id,
		Timestamp: timestamp,
		Actor:     actor,
		Node:      node,
		Platform:  platform,
		TxHash:    txHash,
		PrevHash:  prevHash,
		BlockHash: blockHash,
		Status:    status,
	}

	evidenceBytes, err := json.Marshal(evidence)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, evidenceBytes)
}

// ReadEvidence retrieves evidence from the ledger state
func (c *EvidenceContract) ReadEvidence(ctx contractapi.TransactionContextInterface, id string) (*Evidence, error) {
	evidenceBytes, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if evidenceBytes == nil {
		return nil, fmt.Errorf("the evidence %s does not exist", id)
	}

	var evidence Evidence
	err = json.Unmarshal(evidenceBytes, &evidence)
	if err != nil {
		return nil, err
	}

	return &evidence, nil
}

// EvidenceExists returns true if evidence with given ID exists in world state
func (c *EvidenceContract) EvidenceExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	evidenceBytes, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return evidenceBytes != nil, nil
}

// VerifyEvidence validates stored ledger evidence against a recalculated hash
func (c *EvidenceContract) VerifyEvidence(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	evidence, err := c.ReadEvidence(ctx, id)
	if err != nil {
		return false, err
	}

	computed := c.ComputeHash(evidence.PrevHash, evidence.TxHash, evidence.Timestamp, evidence.Actor, evidence.Node, evidence.Platform, evidence.Status)
	return computed == evidence.BlockHash, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&EvidenceContract{})
	if err != nil {
		log_err := fmt.Sprintf("Error creating Evidence contract chaincode: %s", err)
		panic(log_err)
	}

	if err := chaincode.Start(); err != nil {
		log_err := fmt.Sprintf("Error starting Evidence contract chaincode: %s", err)
		panic(log_err)
	}
}
