import boto3
import os

class DataFetcher:
    def __init__(self):
        """
        Initialize the DataFetcher with S3 client.
        """
        self.s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                      region_name=os.getenv('AWS_REGION'))

    def fetch(self, processed_files=[]):
        """
        Fetch unprocessed raw files from S3 bucket.

        Parameters:
            processed_files (list): List of file names that have already been processed.

        Returns:
            list: List of raw data files fetched from S3.
        """
        bucket_name = os.getenv('S3_BUCKET_NAME')
        unprocessed_files = []
        
        try:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket_name)['Contents']
            for obj in s3_objects:
                file_name = obj['Key']
                if file_name not in processed_files:
                    file_data = self.s3_client.get_object(Bucket=bucket_name, Key=file_name)['Body'].read()
                    unprocessed_files.append({'name': file_name, 'data': file_data})
        except Exception as e:
            print(f"Error fetching data from S3: {e}")

        return unprocessed_files
