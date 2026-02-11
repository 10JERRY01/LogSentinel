# LogSentinel: User Manual

## 📋 Prerequisites
Before you begin, ensure you have the following installed:
1.  **Go** (Golang): To run the ingestion server.
2.  **Python 3.x**: To run the analytics and traffic generator.
3.  **Git Bash** (for Windows): To execute the shell scripts.

## 🛠️ Installation
1.  **Clone the repository** (if you haven't already).
2.  **Install Python Dependencies**:
    Open a terminal in the project folder and run:
    ```bash
    pip install -r requirements.txt
    ```
    *This installs `pandas`, `scikit-learn`, `requests`, and `joblib`.*

## 🚀 Running the Application

### Step 1: Start the Log Server (Go)
This server listens for incoming logs. It needs to be running constantly.
1.  Open a **new terminal window**.
2.  Navigate to the project folder (`cd c:\LogSentinel`).
3.  Run the server:
    ```bash
    go run ingest.go
    ```
    *You should see: `LogSentinel Server started on :8080`*
    > **Note**: Keep this terminal open.

### Step 2: Generate Traffic (Python)
We will simulate a mix of normal user activity and cyber-attacks.
1.  Open a **second terminal window**.
2.  Navigate to the project folder.
3.  Run the generator:
    ```bash
    python.exe traffic_generator.py
    ```
    *You will see logs being sent: `[SENT] INFO: User login successful...`*
    *This script sends 50 log entries to your Go server.*

### Step 3: Run the Pipeline (Bash)
Now we trigger the ETL (Extract, Transform, Load) process. This script checks the log buffer size, rotates the file if it's full, and runs the ML analysis.
1.  In the **second terminal** (or a third one), run:
    ```bash
    bash pipeline.sh
    ```
    
### ✅ What to expect
-   **Output**: You will see messages about "Rotating logs", "Moving to HDFS", and finally an "Analysis Report" from Python.
-   **Anomalies**: If attacks were generated, the script will print `[ALERT] Detected X anomalies!` and list them.
-   **CSV Report**: A file named `anomalies.csv` will be created/updated with the details of any detected threats.

## 🧪 Troubleshooting
-   **"python not found"**: Ensure you are running `python` or `python.exe` correctly. The `pipeline.sh` is configured to use `python.exe` for Windows compatibility.
-   **"Connection refused"**: Make sure the Go server (Step 1) is running and listening on port 8080.
-   **"No log file found"**: You must generate traffic (Step 2) before running the pipeline. The pipeline only runs if the log buffer has data.
