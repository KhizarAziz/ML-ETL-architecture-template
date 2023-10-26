class ETLManager:
    def __init__(self, config):
        """Initialize ETL Manager with pipeline configuration."""
        self.config = config
        # Initialize other components like Data Fetcher, Preprocessor, etc.

    def run(self):
        """Orchestrate the ETL pipeline."""
        self.check_new_data()
        self.fetch_data()
        self.preprocess_data()
        self.train_model()
        self.run_inference()
        self.postprocess_data()

    def check_new_data(self):
        """Check for availability of new raw data batches."""
        # Logic here

    def fetch_data(self):
        """Fetch new raw data."""
        # Logic here

    def preprocess_data(self):
        """Preprocess raw data."""
        # Logic here

    def train_model(self):
        """Train model if sufficient data is available."""
        # Logic here

    def run_inference(self):
        """Run inference on new preprocessed data."""
        # Logic here

    def postprocess_data(self):
        """Postprocess inference results and save to Postgres."""
        # Logic here
