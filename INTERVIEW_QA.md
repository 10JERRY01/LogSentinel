# LogSentinel: Interview Preparation Guide

## 🟢 Section 1: Go (Golang) & Backend
**Q1: Why did you use `sync.Mutex` in `ingest.go`?**
**A:** `ingest.go` is a multi-threaded web server. Multiple requests can hit the `/api/log` endpoint simultaneously. Without a mutex (lock), two goroutines might try to write to the file at the exact same time, causing data corruption or mixed-up lines. `mutex.Lock()` ensures only one goroutine writes at a time.

**Q2: What is a Goroutine?**
**A:** A goroutine is a lightweight thread managed by the Go runtime. They are cheaper than OS threads. Every HTTP request handled by `http.HandleFunc` in Go is processed in its own goroutine automatically.

**Q3: How does `defer` work in your code?**
**A:** I used `defer file.Close()` and `defer mutex.Unlock()`. This ensures that the file is closed and the lock is released *no matter what*, even if the function returns early or encounters an error. It prevents resource leaks and deadlocks.

**Q4: Why `json.NewDecoder` instead of `json.Unmarshal`?**
**A:** `json.NewDecoder` reads directly from the stream (`r.Body`), which is more memory-efficient for HTTP requests than reading the entire body into a byte slice and then using `Unmarshal`.

**Q5: What are Struct Tags (e.g., `` `json:"service"` ``)?**
**A:** They tell the JSON encoder/decoder how to map struct fields to JSON keys. For example, it maps the Go field `Service` (capitalized for export) to the lowercase JSON key `"service"`.

**Q6: What happens if the server crashes?**
**A:** Since we are buffering to a local file (`access_logs_buffer.json`), any data already written to disk is safe. Data currently in memory would be lost. In a production system, we might use a message queue (Kafka) to prevent this.

**Q7: Usage of `os.OpenFile` flags?**
**A:** I used `os.O_APPEND|os.O_CREATE|os.O_WRONLY`. This ensures we add to the end of the file (Append), create it if it doesn't exist (Create), and only write to it (Write Only).

**Q8: Explain the `context` package in Go (even if not used here).**
**A:** `context` is used to carry deadlines, cancellation signals, and request-scoped values across API boundaries and goroutines. It's crucial for efficiently cancelling long-running requests.

**Q9: Difference between Arrays and Slices?**
**A:** Arrays have a fixed size. Slices are dynamic pointers to arrays. In my code, I mostly used slices (implicitly) or standard libraries that usage slices.

**Q10: Error handling philosophy in Go?**
**A:** Go treats errors as values, not exceptions. I checked `if err != nil` after every I/O operation to handle failures explicitly, which is the idiomatic Go way.

**Q11: What is `log.Fatal`?**
**A:** It prints the error message and immediately terminates the program with `os.Exit(1)`. I used it for the server startup failure, as the program cannot proceed without the port.

**Q12: Public vs Private in Go?**
**A:** Capitalized fields/functions (e.g., `LogEntry`) are Exported (Public). Lowercase ones are unexported (Private). I needed `LogEntry` to be public so the `json` package could access it.

**Q13: Why define a Struct for logs?**
**A:** It provides type safety. It ensures that we only accept data that matches our expected schema, rather than dealing with unstructured interfaces.

**Q14: How would you scale this Go server?**
**A:** Go scales vertically well. For horizontal scaling, I would put a Load Balancer (Nginx) in front of multiple instances of this server.

**Q15: What is `defer` execution order?**
**A:** LIFO (Last In, First Out). If I had multiple defers, the last one defined would run first.

---

## 🟡 Section 2: Bash & Linux Scripting
**Q1: What does `#!/bin/bash` mean?**
**A:** It's the "Shebang". It tells the operating system which interpreter to use to execute the script.

**Q2: Explanation of `wc -c < file`?**
**A:** `wc -c` counts bytes. The `<` builds a redirection, feeding the file content to stdin. This prevents `wc` from printing the filename, giving exactly the number we need.

**Q3: How did you perform the file rotation atomically?**
**A:** I used `mv`. On POSIX systems, `mv` (rename) within the same filesystem is atomic. This means a reading process will either see the old filename or the new one, never a half-moved file.

**Q4: Difference between Cron and a loop?**
**A:** A loop runs continuously and consumes CPU while waiting (unless sleeping). Cron is a system daemon that triggers jobs at specific times. For this demo, manual triggering mimics a Cron job.

**Q5: What is `chmod +x`?**
**A:** It changes the file mode bits to make the file "Executable" for all users (User, Group, Others).

**Q6: What is `$?` in Bash?**
**A:** It holds the exit status of the most recently executed command. `0` means success, anything else means error.

**Q7: Explain Pipes (`|`)?**
**A:** A pipe passes the standard output (stdout) of the command on the left to the standard input (stdin) of the command on the right. E.g., `wc -c | tr -d ' '`.

**Q8: What does `tr -d ' '` do?**
**A:** `tr` stands for Translate (or Trim). `-d` deletes the specified character (space). I used it to clean up the output of `wc`.

**Q9: Difference between single quotes `'` and double quotes `"`?**
**A:** Variables inside double quotes are expanded (replaced with values). Variables inside single quotes are treated literally as text.

**Q10: What is HDFS?**
**A:** Hadoop Distributed File System. Ideally, it splits large files across multiple machines. In my script, `mkdir -p hdfs_simulated_storage` mimics the concept of a separate "Data Lake".

**Q11: How do you debug a bash script?**
**A:** You can run it with `bash -x pipeline.sh` to see a trace of every command being executed.

**Q12: What is `STDERR` vs `STDOUT`?**
**A:** `STDOUT` (1) is for normal output. `STDERR` (2) is for errors. You can redirect them separately, e.g., `2> error.log`.

**Q13: How to check if a file exists?**
**A:** `if [ -f "filename" ]; then ... fi`. `-f` checks for a regular file. `-d` checks for a directory.

**Q14: Why use variables like `$HDFS_DIR`?**
**A:** Hardcoding paths is bad practice. Using variables at the top of the script makes it maintainable and easy to change configuration.

**Q15: What is `nohup`?**
**A:** It allows a process to keep running even after the user logs out. Useful for long-running scripts.

---

## 🔵 Section 3: Python & Machine Learning
**Q1: What is the "Single Responsibility Principle"?**
**A:** It's a clean code principle where a class should have only one reason to change. I separated `LogLoader` (loading data), `LogPreprocessor` (cleaning data), and `AnomalyDetector` (ML logic) into different classes.

**Q2: Why `IsolationForest`?**
**A:** It is an unsupervised algorithm specifically designed for anomaly detection. Unlike other models that try to profile "normal" data (density estimation), Isolation Forest explicitly isolates anomalies by randomly splitting data points. Anomalies are easier to isolate (require fewer splits).

**Q3: Supervised vs Unsupervised Learning?**
**A:** Supervised needs labeled data (Input + Target Answer). Unsupervised (like this project) looks for patterns in unlabeled data.

**Q4: Explain the Feature Engineering you did.**
**A:** Models need numbers, not text.
1.  **Level Score**: Mapped INFO->1, ERROR->10 to quantify severity.
2.  **Message Length**: Detected that long messages often correlate with SQL injections or stack traces.
3.  **Hour**: Extracted time to find activity at unusual hours.

**Q5: What is `pandas`?**
**A:** A powerful library for data manipulation. It provides the **DataFrame** structure, which is like a programmable Excel spreadsheet with labeled rows and columns.

**Q6: What is a "List Comprehension"?**
**A:** A concise way to create lists in Python. E.g., `[x for x in data if x > 0]`. I used it to filter files.

**Q7: Explain `os.path.join`?**
**A:** It intelligently joins path components (e.g., "folder" and "file.txt") using the correct separator for the OS (`/` for Linux, `\` for Windows). It makes the code cross-platform.

**Q8: What does `if __name__ == "__main__":` do?**
**A:** It checks if the script is being run directly. If the file is imported as a module by another script, the code inside this block won't run.

**Q9: What is `joblib`?**
**A:** A tool for efficiently saving and loading Python objects, especially large NumPy arrays or ML models (`model.pkl`).

**Q10: What is Overfitting?**
**A:** When a model learns the training data *too* well, including noise, and fails to generalize to new data.

**Q11: Why fillna(0)?**
**A:** ML models cannot handle missing values (`NaN`). `fillna(0)` replaces them with a zero, ensuring the math operations don't crash.

**Q12: Use of `try/except`?**
**A:** Robustness. If a file is missing or the model fails, the script catches the error and prints a friendly message instead of crashing with a stack trace.

**Q13: What does `apply(len)` do in Pandas?**
**A:** It applies the `len` function to every row in the column efficiently.

**Q14: Explain `random_state=42`?**
**A:** It sets the seed for the random number generator. It ensures that every time we run the model training, we get the exact same results, making the experiment reproducible.

**Q15: How would you improve this model?**
**A:** I would add **TF-IDF** (Term Frequency-Inverse Document Frequency) to analyze the actual *words* in the log messages, not just the length.
