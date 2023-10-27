import os
import psycopg2
import datetime

class StateManager:
    def __init__(self):
        # Database connection setup
        self.conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        self.cursor = self.conn.cursor()

    def get_state(self, key):
        """Retrieve a specific state by its key."""
        self.cursor.execute("SELECT value FROM etl_state_table WHERE key = %s", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_state(self, key, value):
        """Set or update a specific state by its key."""
        self.cursor.execute("INSERT INTO etl_state_table (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s", (key, value, value))
        self.conn.commit()

    def get_processed_file_ids(self):
        """Retrieve the processed file IDs."""
        return self.get_state("processed_file_ids")

    def set_processed_file_ids(self, ids):
        """Set the processed file IDs."""
        self.set_state("processed_file_ids", ids)

    def is_data_sufficient_for_training(self):
        """Check if there's enough data for training (e.g. 2 weeks)."""
        last_processed_date = self.get_state("last_processed_date")
        if last_processed_date:
            difference = datetime.datetime.now() - datetime.datetime.strptime(last_processed_date, "%Y-%m-%d")
            return difference.days >= 14
        return False

    def get_latest_trained_model(self):
        """Retrieve the latest trained model."""
        return self.get_state("latest_trained_model")

    def set_latest_trained_model(self, model_name):
        """Set the latest trained model."""
        self.set_state("latest_trained_model", model_name)

    def get_inferenced_data_ids(self):
        """Retrieve IDs of data that has already been inferenced."""
        return self.get_state("data_inferenced")

    def set_inferenced_data_ids(self, ids):
        """Set IDs of data that has already been inferenced."""
        self.set_state("data_inferenced", ids)

    def close(self):
        # Close database connection
        self.cursor.close()
        self.conn.close()

# Usage:
# state_manager = StateManager()
# ... operations ...
# state_manager.close()
