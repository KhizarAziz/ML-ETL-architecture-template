import boto3
import os
import pandas as pd
from sklearn.externals import joblib

class TrainingManager:
    def __init__(self, state_manager):
        """
        Initializes the TrainingManager by setting up S3 client and loading configurations.
        """
        # Load AWS credentials from environment variables
        aws_access_key = os.environ.get('AWS_ACCESS_KEY')
        aws_secret_key = os.environ.get('AWS_SECRET_KEY')

        self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        self.state_manager = state_manager
        # Placeholder for your model, adjust accordingly
        self.model = None

    def train(self, preprocessed_data_ids, model_parameters):
        """
        Trains the model using the provided data.

        Parameters:
            preprocessed_data_ids (list): List of preprocessed data IDs to be used for training.
            model_parameters (dict): Parameters for the model training.
        """
        data = self._load_data_for_training(preprocessed_data_ids)

        # Implement your training logic here using self.model and the data

        # After training:
        model_id = "model_name_or_id"  # Placeholder for model ID or name
        self._store_trained_model(model_id)
        
        # Store the training data used
        self._store_training_data(preprocessed_data_ids, model_id)

        # Update state in the state_manager
        # Placeholder for your model's score
        model_score = "YOUR_MODEL_SCORE"
        self.state_manager.set_state("trained_model", model_id)
        self.state_manager.set_state("trained_model_score", model_score)

    def _load_data_for_training(self, preprocessed_data_ids):
        """
        Load the preprocessed data for training.

        Parameters:
            preprocessed_data_ids (list): List of preprocessed data IDs to be loaded.

        Returns:
            DataFrame: Aggregated data for training.
        """
        frames = []

        for data_id in preprocessed_data_ids:
            data_path = f"Preprocessed/StateVectors_{data_id}"
            local_data_path = f"./StateVectors_{data_id}.csv"
            self.s3_client.download_file("YOUR_BUCKET_NAME_2", data_path, local_data_path)
            
            frames.append(pd.read_csv(local_data_path))

        return pd.concat(frames, ignore_index=True)

    def _store_trained_model(self, model_id):
        """
        Stores the trained model to AWS S3.

        Parameters:
            model_id (str): ID or name of the trained model.
        """
        model_path = f"Trained_Models/{model_id}"
        local_model_path = f"./{model_id}"
        
        joblib.dump(self.model, local_model_path)
        self.s3_client.upload_file(local_model_path, "YOUR_BUCKET_NAME_2", model_path)

    def _store_training_data(self, preprocessed_data_ids, model_id):
        """
        Store the training data used in a subfolder for the corresponding model.

        Parameters:
            preprocessed_data_ids (list): List of preprocessed data IDs used for training.
            model_id (str): ID or name of the trained model.
        """
        for data_id in preprocessed_data_ids:
            source_path = f"Preprocessed/StateVectors_{data_id}"
            destination_path = f"Trained_Models/{model_id}/TrainingData/StateVectors_{data_id}"

            self.s3_client.copy_object(Bucket="YOUR_BUCKET_NAME_2", CopySource=source_path, Key=destination_path)
