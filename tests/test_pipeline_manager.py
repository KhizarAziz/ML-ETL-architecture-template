import unittest
from unittest.mock import patch
from etl import PipelineManager

class PipelineManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.pipeline_manager = PipelineManager()

    @patch('etl.PipelineManager.preprocess_data')
    def test_preprocess_data_call(self, mock_preprocess_data):
        new_data = [...]  # Sample new data
        self.pipeline_manager.preprocess_data(new_data)
        mock_preprocess_data.assert_called_once_with(new_data)

    @patch('etl.PipelineManager.start_training')
    def test_start_training_call(self, mock_start_training):
        configs = {'config_key': 'value'}  # Example configs
        self.pipeline_manager.start_training(configs)
        mock_start_training.assert_called_once_with(configs)

    @patch('etl.PipelineManager.start_inference')
    def test_start_inference_call(self, mock_start_inference):
        new_data = [...]  # Sample new data for inference
        self.pipeline_manager.start_inference(new_data)
        mock_start_inference.assert_called_once_with(new_data)

    # More test cases based on additional methods or functionalities of the PipelineManager

