package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

// Define the structure of our log data
// This matches the JSON we expect to receive
type LogEntry struct {
	Service   string `json:"service"`
	Level     string `json:"level"`
	Message   string `json:"message"`
	Timestamp string `json:"timestamp"`
}

// Mutex to ensure safe concurrent writing to the file
var fileMutex sync.Mutex

func handleLog(w http.ResponseWriter, r *http.Request) {
	// Only allow POST requests
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var entry LogEntry
	// Decode the JSON body request into our struct
	err := json.NewDecoder(r.Body).Decode(&entry)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Add a received timestamp server-side
	entry.Timestamp = time.Now().Format(time.RFC3339)

	// Prepare the line to write (JSON format)
	logLine, _ := json.Marshal(entry)

	// CRITICAL: Lock the file writing operation
	// Go handles requests concurrently. Without this lock, two requests
	// writing at the same time would corrupt the file.
	fileMutex.Lock()
	defer fileMutex.Unlock()

	f, err := os.OpenFile("access_logs_buffer.json", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Printf("Error opening file: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer f.Close()

	if _, err := f.Write(logLine); err != nil {
		log.Printf("Error writing to file: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	if _, err := f.WriteString("\n"); err != nil {
		log.Printf("Error writing newline: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	// Send success response
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Log Received")
}

func main() {
	http.HandleFunc("/api/log", handleLog)
	fmt.Println("LogSentinel Server started on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
