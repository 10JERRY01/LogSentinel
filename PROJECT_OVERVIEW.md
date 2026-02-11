# LogSentinel: Project Overview

## 🚀 The Elevator Pitch
**LogSentinel** is a full-stack automated threat detection pipeline designed to handle high-velocity log data. It simulates a modern data engineering workflow where logs are ingested by a high-performance **Go** server, managed and rotated by **Shell** scripts (simulating HDFS movement), and analyzed for security anomalies using **Python** machine learning algorithms.

## 🏗️ Architecture & Design Decisions

### 1. Ingestion Layer (Go)
**Why Go?**
I chose Go (Golang) for the ingestion layer because of its raw performance and native concurrency support. In a real-world scenario, a log server might receive thousands of requests per second.
- **Key Feature**: Used `sync.Mutex` to safely write to a shared file from multiple concurrent HTTP requests, preventing race conditions.
- **Role**: Validates incoming JSON, timestamps it, and buffers it to disk.

### 2. Orchestration Layer (Bash)
**Why Bash?**
Bash is the standard for "glue code" in Linux environments. It binds the system together without the overhead of compiled languages.
- **Key Feature**: Use of `wc -c` for efficient file size checking and atomic `mv` operations to rotate logs without losing data.
- **Role**: Monitors the buffer size. Once it hits a threshold (simulating a block size), it "rotates" the file (renames it) and moves it to a simulated separate storage cluster (HDFS directory).

### 3. Analytics Layer (Python & Machine Learning)
**Why Python?**
Python is the industry standard for Data Science and ML due to its rich ecosystem (Pandas, Scikit-learn).
- **Key Feature**: Implemented an **Isolation Forest** algorithm. This is an "Unsupervised" learning model, meaning it doesn't need labeled "good" or "bad" data beforehand. It learns the "shape" of normal data and flags statistical outliers (anomalies).
- **Feature Engineering**: The raw logs are text. I converted them into numerical features the model can understand:
    - **Risk Score**: Mapped `INFO` to 1, `ERROR` to 10.
    - **Message Length**: Unusually long messages often indicate stack traces or SQL injection attacks.
    - **Time**: Extracted the hour to find temporal anomalies.

## 💡 What this project demonstrates
1.  **Full Data Pipeline**: From API ingestion -> Buffering -> ETL (Moving) -> Analytics.
2.  **Polyglot Programming**: Seamlessly integrating Go, Bash, and Python.
3.  **Concurrency Control**: Handling shared resources in a multi-threaded web server.
4.  **Security Awareness**: Detecting SQL injections and XSS attacks using ML.
5.  **Clean Code Principles**: Single Responsibility Principle (SRP) in Python classes.

## 🔮 Future Improvements
-   **Dockerization**: Containerize each component for easier deployment.
-   **Real HDFS**: Connect to a real Hadoop cluster instead of a local folder.
-   **Dashboard**: Visualize `anomalies.csv` using a frontend framework (React) or a tool like Grafana.
