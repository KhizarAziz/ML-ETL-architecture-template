import boto3
import os
import pandas as pd
from joblib import load

class InferenceEngine:
    def __init__(self):
        """
        Initializes the InferenceEngine by setting up S3 client and loading configurations.
        """
        # Load AWS credentials from environment variables
        aws_access_key = os.environ.get('AWS_ACCESS_KEY')
        aws_secret_key = os.environ.get('AWS_SECRET_KEY')

        self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        self.model = None  # Placeholder for the loaded model

    def load_model(self, model_id):
        """
        Loads the best model from AWS S3 Bucket.

        Parameters:
            model_id (str): ID or name of the best model to be loaded.
        """
        bucket_name = "YOUR_BUCKET_NAME_2"  # Adjust this as necessary
        model_path = f"Trained_Models/{model_id}"
        
        # Download the model from S3 to a local path
        local_model_path = f"./{model_id}"
        self.s3_client.download_file(bucket_name, model_path, local_model_path)
        
        # Load the model
        self.model = load(local_model_path)

    def run_inference(self, best_model, asset_uuids, inferenced_data_ids):
        """
        Run inference on the new data batches that haven't been inferenced before.

        Parameters:
            best_model (str): ID of the best model to be loaded.
            asset_uuids (list): List of asset UUIDs that need inference.
            inferenced_data_ids (list): List of data IDs that have already been inferenced.

        Returns:
            list: IDs of the batches that have been inferenced in this run.
        """
        self.load_model(best_model)

        # Filter out asset_uuids that have already been inferenced
        assets_to_inference = [uuid for uuid in asset_uuids if uuid not in inferenced_data_ids]

        inferred_data = []
        for asset_uuid in assets_to_inference:
            # Load the preprocessed data for this asset_uuid from S3
            data = self._load_data_from_s3(asset_uuid)
            
            # Inference logic here using self.model on the data
            # results = self.model.predict(data)

            # Store results back to S3
            # self._store_results_to_s3(asset_uuid, results)

            inferred_data.append(asset_uuid)

        return inferred_data

    def _load_data_from_s3(self, asset_uuid):
        """
        Load preprocessed data for a given asset UUID from AWS S3.

        Parameters:
            asset_uuid (str): Asset UUID of the data to be loaded.

        Returns:
            DataFrame: Loaded data for the given asset UUID.
        """
        bucket_name = "YOUR_BUCKET_NAME_2"  # Adjust this as necessary
        data_path = f"Preprocessed/StateVectors_{asset_uuid}"  # Added prefix "StateVectors_" as per requirements

        local_data_path = f"./StateVectors_{asset_uuid}.csv"
        self.s3_client.download_file(bucket_name, data_path, local_data_path)
        
        return pd.read_csv(local_data_path)

    def _store_results_to_s3(self, asset_uuid, results):
        """
        Store the inference results for a given asset UUID to AWS S3.

        Parameters:
            asset_uuid (str): Asset UUID of the data.
            results (DataFrame): Inference results to be stored.
        """
        bucket_name = "YOUR_BUCKET_NAME_2"  # Adjust this as necessary
        results_path = f"Inference_Output/{asset_uuid}"

        # Assuming results is a DataFrame
        results.to_csv(f"./results_{asset_uuid}.csv", index=False)
        self.s3_client.upload_file(f"./results_{asset_uuid}.csv", bucket_name, results_path)
