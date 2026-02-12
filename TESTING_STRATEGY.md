# Testing & QA Strategy

## 🧪 Testing Overview
In this project, I implemented a robust testing strategy covering both **Unit Tests** (validating individual components) and **Integration Tests** (validating the whole pipeline). This ensures reliability in a production environment.

## 🐍 Python Unit Tests (`detect.py`)
I used the `unittest` framework to verify the ML pipeline.
### Key Test Cases:
1.  **Corrupted Data Handling**:
    -   *Scenario*: What if a log file has a half-written JSON line?
    -   *Test*: `test_load_malformed_json_lines` creates a dummy file with garbage text.
    -   *Result*: Verified that `LogLoader` skips the bad line, logs a warning, and continues processing the valid lines. **Resiliency is key.**
2.  **Missing Features**:
    -   *Scenario*: What if the log format changes and "level" is missing?
    -   *Test*: `test_preprocess_missing_columns`.
    -   *Result*: The preprocessor now sets a default risk score of `0` instead of crashing with a `KeyError`.
3.  **Model Mocking**:
    -   *Scenario*: We don't want to wait for a real training cycle during tests.
    -   *Mocking*: Checked that `AnomalyDetector` can initialize and save a model file correctly.

## 🐹 Go Unit Tests (`ingest.go`)
I used Go's built-in `testing` package and `httptest` to test the API handler without spinning up a real server.
### Key Test Cases:
1.  **Invalid JSON**:
    -   *Scenario*: A hacker sends `{ "broken...`.
    -   *Test*: `TestInvalidJSON`.
    -   *Result*: Endpoint returns `400 Bad Request`.
2.  **Concurrency** (Concept):
    -   I explained how `sync.Mutex` prevents data corruption, which is verified by load testing (using `traffic_generator.py`) rather than simple unit tests.

## 🚨 Edge Cases Handled
During testing, I identified and fixed the following potential crashes:
1.  **Empty Files**: If the log buffer was rotated but empty, the standard `json.load` would fail. I added a check for `if not data`.
2.  **Date Parsing Errors**: If a timestamp is malformed, `pd.to_datetime` now uses `errors='coerce'` to handle it gracefully (setting it to NaT/0) instead of halting the pipeline.
3.  **Recursion** (Future Proofing): Ensured the `pipeline.sh` doesn't try to process its own output logs.

## 🗣️ Interview Explanation Script
*"My testing philosophy is to assume inputs will be malicious or broken. I wrote unit tests for the Python data loader to ensure that one bad log line doesn't crash the entire analytics job. For the Go server, I used `httptest` to verify that we reject invalid JSON immediately with a 400 error, protecting the system from garbage data."*
