# LogSentinel 🛡️

A simulated excessive log anomaly detection pipeline.

## Project Structure
- `ingest.go`: High-performance log ingestion server (Go).
- `pipeline.sh`: Data moving and batch processing script (Bash).
- `detect.py`: Machine Learning anomaly detection (Python/scikit-learn).
- `traffic_generator.py`: Tool to simulate normal and malicious traffic.

## Setup

1. **Prerequisites**
   - Go (Golang) installed
   - Python 3.x installed
   - Git Bash (if on Windows)

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Storage**
   Ensure the simulated HDFS directory exists:
   ```bash
   mkdir -p hdfs_simulated_storage
   ```

## Usage

### 1. Start the Ingestion Server
Open a terminal and run:
```bash
go run ingest.go
```
*Server runs on port 8080.*

### 2. Generate Traffic
Open a second terminal. You can use the generator to send 50 logs with ~10% anomalies:
```bash
python traffic_generator.py
```

### 3. Run the Pipeline
In the same second terminal, run the pipeline checks. This mimics a cron job.
```bash
./pipeline.sh
```
*If logs exceed the threshold (100 bytes for demo), they are moved to storage and analyzed.*

## How it Works
1. **Ingest**: Apps POST logs to `localhost:8080/api/log`. Go server appends them to `access_logs_buffer.json`.
2. **Pipeline**: `pipeline.sh` checks file size. If large enough -> rotates file -> moves to `hdfs_simulated_storage`.
3. **Detect**: `detect.py` picks up the latest file, extracts features (Message Length, Error Level, Hour), and uses an Isolation Forest model to flag anomalies. Detected anomalies are saved to `anomalies.csv`.
