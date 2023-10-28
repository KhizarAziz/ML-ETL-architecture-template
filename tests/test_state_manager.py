import unittest
from etl import state_manager

class StateManagerTestCase(unittest.TestCase):

    def test_get_state_returns_data(self):
        state_key = "some_key"  # Replace with a valid key from your state manager
        result = state_manager.get_state(state_key)
        self.assertIsNotNone(result, f"State for key {state_key} should not be None")

    def test_update_state_changes_value(self):
        state_key = "some_key"
        new_value = "new_value"
        state_manager.update_state(state_key, new_value)
        result = state_manager.get_state(state_key)
        self.assertEqual(result, new_value, f"Updated value for key {state_key} should be {new_value}")
