
import unittest
import json
import logging
import os
import shutil
import pandas as pd
import numpy as np
import tempfile
from io import StringIO
from unittest.mock import MagicMock, patch

# --- Assuming the classes are in detect.py ---
try:
    from detect import LogLoader, LogPreprocessor, AnomalyDetector
except ImportError:
    print("Warning: detect.py not found. Tests will fail.")

class TestLogLoader(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.loader = LogLoader(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_valid_file(self):
        log_file = os.path.join(self.test_dir, "test_log.json")
        with open(log_file, "w") as f:
            f.write('{"service": "test", "level": "INFO", "message": "hello", "timestamp": "2023-01-01T00:00:00Z"}\n')
        
        df = self.loader.load_latest_file()
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)

    def test_load_malformed_json_lines(self):
        log_file = os.path.join(self.test_dir, "corrupt_log.json")
        with open(log_file, "w") as f:
            f.write('{"service": "ok", "level": "INFO"}\n')
            f.write('CORRUPT DATA LINE\n')
            f.write('{"service": "ok2", "level": "WARN"}\n')
        
        df = self.loader.load_latest_file()
        self.assertEqual(len(df), 2)

    def test_empty_directory_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            self.loader.load_latest_file()

class TestLogPreprocessor(unittest.TestCase):
    def setUp(self):
        self.processor = LogPreprocessor()

    def test_preprocess_valid_data(self):
        data = {
            'level': ['INFO', 'ERROR'],
            'message': ['Short', 'Long message here'],
            'timestamp': ['2023-01-01T10:00:00Z', '2023-01-01T11:00:00Z']
        }
        df = pd.DataFrame(data)
        features = self.processor.preprocess(df)
        self.assertEqual(len(features), 2)

    def test_preprocess_missing_columns(self):
        data = {
            'message': ['Test'],
            'timestamp': ['2023-01-01T10:00:00Z']
        }
        df = pd.DataFrame(data)
        features = self.processor.preprocess(df)
        self.assertEqual(len(features), 1)
        self.assertEqual(features.iloc[0]['level_score'], 0) # Default since level missing

class TestAnomalyDetector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.test_dir, "model.pkl")
        self.detector = AnomalyDetector(model_path=self.model_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_train_and_predict(self):
        features = pd.DataFrame({
            'level_score': [1, 1, 10], 
            'message_len': [10, 12, 100], 
            'hour': [10, 11, 23]
        })
        self.detector.train_mock_model()
        self.assertTrue(os.path.exists(self.model_path))
        preds = self.detector.predict(features)
        self.assertEqual(len(preds), 3)

class TestLargeScale(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.loader = LogLoader(self.test_dir)
        self.processor = LogPreprocessor()
        self.detector = AnomalyDetector(model_path=os.path.join(self.test_dir, "model.pkl"))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_42_example_jsons(self):
        # Generate 42 log entries
        logs = []
        for i in range(42):
            logs.append(json.dumps({
                "service": f"service_{i % 5}",
                "level": "INFO" if i % 2 == 0 else "ERROR",
                "message": f"This is log message number {i}",
                "timestamp": "2023-01-01T10:00:00Z"
            }))
        
        # Write to file
        log_file = os.path.join(self.test_dir, "large_test.json")
        with open(log_file, "w") as f:
            f.write("\n".join(logs))

        # Test Pipeline
        df = self.loader.load_latest_file()
        self.assertEqual(len(df), 42)
        
        features = self.processor.preprocess(df)
        self.assertEqual(len(features), 42)
        
        # Train & Predict
        self.detector.train_mock_model()
        predictions = self.detector.predict(features)
        self.assertEqual(len(predictions), 42)
        print(f"\n[TEST] Successfully processed {len(predictions)} logs.")

if __name__ == '__main__':
    unittest.main()
