#!/bin/bash

# Configuration
LOG_FILE="access_logs_buffer.json"
HDFS_DIR="./hdfs_simulated_storage"
THRESHOLD_SIZE=100 # Size in bytes (set low for testing, real world would be 10MB)

echo "--- LogSentinel Pipeline Started ---"

# Check if log file exists
if [ -f "$LOG_FILE" ]; then
    # Get file size (cross-platform way for Linux/Mac)
    # If using Windows Git Bash, stat might behave differently, so we use wc -c
    FILE_SIZE=$(wc -c < "$LOG_FILE" | tr -d ' ')
    
    echo "Current Log Size: $FILE_SIZE bytes"

    if [ "$FILE_SIZE" -gt "$THRESHOLD_SIZE" ]; then
        echo "[ALERT] File size limit exceeded. Rotating logs..."
        
        # Generate timestamp
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        NEW_FILENAME="log_$TIMESTAMP.json"
        
        # Rename the file (Atomic operation effectively)
        mv "$LOG_FILE" "$NEW_FILENAME"
        
        # Move to 'HDFS'
        mv "$NEW_FILENAME" "$HDFS_DIR/"
        
        echo "[SUCCESS] Log moved to HDFS: $HDFS_DIR/$NEW_FILENAME"
        
        # Create a new empty buffer file just in case, though the Go server creates it auto.
        touch "$LOG_FILE"
        
        # Here is where we would trigger the Python ML script
        # python3 detect_anomalies.py $HDFS_DIR/$NEW_FILENAME
        
    else
        echo "[INFO] File size is within limits. No action taken."
    fi
else
    echo "[WARNING] No log file found. Waiting for data..."
fi