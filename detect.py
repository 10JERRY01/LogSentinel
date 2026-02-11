import json
import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# --- Class 1: The Data Loader (Single Responsibility Principle) ---
class LogLoader:
    """Handles reading data from our simulated HDFS storage."""
    
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def load_latest_file(self):
        """Finds the most recent log file in the directory."""
        files = [os.path.join(self.storage_path, f) for f in os.listdir(self.storage_path) if f.endswith('.json')]
        if not files:
            raise FileNotFoundError("No log files found in storage.")
        
        # Get the latest file based on filename (since it contains timestamp)
        latest_file = max(files, key=lambda f: os.path.basename(f))
        print(f"[INFO] Loading file: {latest_file}")
        
        # Read JSON lines into a list
        data = []
        with open(latest_file, 'r') as f:
            for line in f:
                if line.strip(): # Skip empty lines
                    data.append(json.loads(line))
        
        return pd.DataFrame(data)

# --- Class 2: The Feature Engineer (Data Transformation) ---
class LogPreprocessor:
    """Converts raw text logs into numerical features for ML."""
    
    def preprocess(self, df):
        if df.empty:
            return pd.DataFrame()

        # Feature 1: Map 'Level' to a numerical risk score
        # INFO = 1, WARN = 5, ERROR = 10
        level_map = {'INFO': 1, 'WARN': 5, 'ERROR': 10}
        df['level_score'] = df['level'].map(level_map).fillna(0)

        # Feature 2: Length of the log message (Longer messages might be stack traces)
        df['message_len'] = df['message'].apply(len)

        # Feature 3: Time of day (Hour) - extracted from timestamp
        # We need to handle the timestamp format from Go (RFC3339)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        # Return only the numerical columns for the model
        return df[['level_score', 'message_len', 'hour']]

# --- Class 3: The Brain (Machine Learning Model) ---
class AnomalyDetector:
    """Wraps the Isolation Forest model."""
    
    def __init__(self, model_path='model.pkl'):
        self.model_path = model_path
        self.model = None

    def train_mock_model(self):
        """Trains a model on fake 'normal' data to initialize the system."""
        print("[INFO] Training initial model on synthetic normal data...")
        # Create fake normal data: Mostly INFO logs, short messages
        rng = np.random.RandomState(42)
        X_train = 0.3 * rng.randn(100, 3)
        X_train_data = np.r_[X_train + 2, X_train - 2] # Generate some clusters
        
        # Convert to DataFrame to match feature names
        X_train_df = pd.DataFrame(X_train_data, columns=['level_score', 'message_len', 'hour'])

        self.model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        self.model.fit(X_train_df)
        self.save_model()

    def predict(self, features):
        if not os.path.exists(self.model_path):
            self.train_mock_model()
        else:
            self.model = joblib.load(self.model_path)
        
        # Predict: -1 is anomaly, 1 is normal
        predictions = self.model.predict(features)
        return predictions

    def save_model(self):
        joblib.dump(self.model, self.model_path)

# --- Main Execution Flow ---
if __name__ == "__main__":
    # 1. Setup paths
    HDFS_DIR = "./hdfs_simulated_storage"
    
    try:
        # 2. Instantiate Classes
        loader = LogLoader(HDFS_DIR)
        preprocessor = LogPreprocessor()
        detector = AnomalyDetector()

        # 3. Load & Process Data
        raw_df = loader.load_latest_file()
        features = preprocessor.preprocess(raw_df)

        # 4. Run Detection
        if not features.empty:
            raw_df['anomaly'] = detector.predict(features)
            
            # 5. Report Results
            print("\n--- Analysis Report ---")
            anomalies = raw_df[raw_df['anomaly'] == -1]
            
            if not anomalies.empty:
                print(f"[ALERT] Detected {len(anomalies)} anomalies!")
                print(anomalies[['service', 'level', 'message', 'anomaly']])
                anomalies.to_csv("anomalies.csv", index=False)
                print("[INFO] Anomalies saved to anomalies.csv")
            else:
                print("[SUCCESS] System healthy. No anomalies detected.")
        else:
            print("[WARN] No data to process.")

    except Exception as e:
        print(f"[ERROR] Pipeline failed: {str(e)}")