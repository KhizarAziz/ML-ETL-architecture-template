import json
import schedule
import time
from confluent_kafka import Consumer, KafkaError
from data_fetcher import DataFetcher
from preprocessor import Preprocessor
from state_manager import StateManager
from training_job import TrainingJob
from inference_engine import InferenceEngine
from postprocessor import Postprocessor

class PipelineManager:
    def __init__(self, model_parameters, asset_uuids):
        """
        Initialize PipelineManager with necessary components.
        
        Parameters:
            model_parameters (dict): Dictionary containing the model parameters.
            asset_uuids (list): List of asset UUIDs for which the pipeline is to be run.
        """
        self.data_fetcher = DataFetcher()
        self.preprocessor = Preprocessor()
        self.state_manager = StateManager()
        self.training_job = TrainingJob()
        self.inference_engine = InferenceEngine()
        self.postprocessor = Postprocessor()
        self.model_parameters = model_parameters
        self.asset_uuids = asset_uuids
        

    def listen_to_kafka_topic(self, topic):
        """
        Listens to a specified Kafka topic for new data batches.
        
        Parameters:
            topic (str): Name of the Kafka topic to subscribe to.
        """        
        try:
            consumer = Consumer({
                'bootstrap.servers': 'localhost:9092',
                'group.id': 'pipeline-group',
                'auto.offset.reset': 'latest'
            })
            consumer.subscribe([topic])
        except Exception as e:
            print(f"Error initializing Kafka consumer: {e}")
            return

        while True:
            msg = consumer.poll(1)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Kafka Error: {msg.error()}")
                    break

            self.run_pipeline_for_asset()

    def run_pipeline_for_asset(self):
        """
        Run the pipeline for a given asset UUID.
        
        This method orchestrates the entire pipeline from fetching data to post-processing.
        """

        # fetch unprocessed raw_file_names
        raw_file_names_not_to_fetch = self.state_manager.get_state("processed_raw_file_names")

        # Fetch new data files
        raw_data_files = self.data_fetcher.fetch(raw_file_names_not_to_fetch)
        
        # Update state for fetched data (Optional)
        # self.state_manager.update_state("data_fetched", raw_data_files)
        
        # Preprocess the data
        preprocessed_data_ids = self.preprocessor.process(raw_data_files)
        
        # Update state for preprocessed data
        self.state_manager.update_state("data_preprocessed", preprocessed_data_ids)
        
        # Train model if enough data (e.g 2 weeks)
        if self.state_manager.is_data_sufficient():
            self.training_job.train(preprocessed_data_ids, self.model_parameters)
            
        # Run inference
        best_model = self.state_manager.get_state("best_model")
        inferenced_data_ids = self.state_manager.get_state("data_inferenced")
        inference_results = self.inference_engine.run_inference(best_model, self.asset_uuids,inferenced_data_ids)
        
        # Update state for inference
        self.state_manager.update_state("inference_done", inference_results)
        
        # Post-process results
        inference_data_to_export = self.state_manager.get_state("un_exported_export_results")
        self.postprocessor.process(inference_data_to_export)

def job():
    """
    Scheduled job function that triggers the pipeline for asset data processing.
    """    
    pipeline_manager.run_pipeline_for_asset()

if __name__ == "__main__":
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config.json: {e}")
        exit(1)
    
    model_parameters = config.get("model_parameters")
    asset_uuids = config.get("asset_uuids")
    pipeline_configs = config.get("pipeline_settings")

    if not isinstance(model_parameters, dict) or not isinstance(asset_uuids, list) or not isinstance(pipeline_configs, dict):
        print("Invalid config types")
        exit(1)

    pipeline_manager = PipelineManager(model_parameters, asset_uuids)

    if pipeline_configs.get("listen_to_kafka_topic", False):
        pipeline_manager.listen_to_kafka_topic("new-data-batch")
    else:
        try:
            scheduler_time_minutes = int(pipeline_configs.get('schuler_time_minutes', 10))
        except ValueError:
            print("Invalid scheduler time in config")
            exit(1)
        
        schedule.every(scheduler_time_minutes).minutes.do(job)
        
        while True:
            schedule.run_pending()
            time.sleep(1)