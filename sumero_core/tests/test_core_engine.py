import unittest
import sys
import os

# Add parent directory of 'sumero_core' (which is 'archive') to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # Up 2 levels: sumero_core/tests -> sumero_core -> archive
sys.path.append(project_root)

from sumero_core.engine import run_engine

class TestCoreEngine(unittest.TestCase):
    
    def test_sleep_deprived_user(self):
        """Test Case 1: Bad Sleep (< 6h) -> Sleep Deprived"""
        inputs = {
            "sleep_hours": 5.5,
            "stress_level": 4,
            "resting_hr": 60,
            "age": 30,
            "occupation": "Tester"
        }
        
        result = run_engine(inputs)
        
        self.assertEqual(result["health_state"], "Sleep_Deprived")
        self.assertFalse(result["workout_allowed"])
        self.assertTrue(result["nap_recommended"])
        self.assertEqual(result["recommended_bedtime"], "21:00")
        self.assertIn("LOW_SLEEP", result["reason_codes"])

    def test_under_recovered_high_stress(self):
        """Test Case 2: Good Sleep (7.5h) but High Stress (8) -> Under Recovered"""
        inputs = {
            "sleep_hours": 7.5,
            "stress_level": 8,
            "resting_hr": 65,
            "age": 30,
            "occupation": "CEO"
        }
        
        result = run_engine(inputs)
        
        self.assertEqual(result["health_state"], "Under_Recovered")
        self.assertFalse(result["workout_allowed"]) # Stress blocks workout
        self.assertEqual(result["priority_focus"], "recovery")

    def test_optimal_user(self):
        """Test Case 3: Good Sleep (8h) and Low Stress (3) -> Well Recovered"""
        inputs = {
            "sleep_hours": 8.0,
            "stress_level": 3,
            "resting_hr": 50,
            "age": 25,
            "occupation": "Athlete"
        }
        
        result = run_engine(inputs)
        
        self.assertEqual(result["health_state"], "Well_Recovered")
        self.assertTrue(result["workout_allowed"])
        self.assertEqual(result["recommended_bedtime"], "22:30")

if __name__ == '__main__':
    unittest.main()
