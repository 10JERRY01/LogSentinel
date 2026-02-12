package main

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

// The handler `handleLog` calls `os.OpenFile("access_logs_buffer.json")`.
// In a unit test, we prefer not to write to the real file, but `ingest.go`
// hardcodes the filename.

// For this test, we will let it write to the file but clean it up afterwards.
// This is an integration test approach.

// TestValidLogSubmission ensures that valid JSON is accepted.
func TestValidLogSubmission(t *testing.T) {
	// We don't need to manually create the file, handleLog does it.
	// However, we should clean up created files.
	defer func() {
		os.Remove("access_logs_buffer.json")
	}()

	payload := []byte(`{"service": "test", "level": "INFO", "message": "unit test", "timestamp": "2023-01-01"}`)
	req, err := http.NewRequest("POST", "/api/log", bytes.NewBuffer(payload))
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handleLog)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}
}

// TestInvalidJSON ensures malformed requests are rejected.
func TestInvalidJSON(t *testing.T) {
	payload := []byte(`{"broken_json": `)
	req, err := http.NewRequest("POST", "/api/log", bytes.NewBuffer(payload))
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handleLog)

	handler.ServeHTTP(rr, req)

	// We expect 400 Bad Request
	if status := rr.Code; status != http.StatusBadRequest {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusBadRequest)
	}
}
