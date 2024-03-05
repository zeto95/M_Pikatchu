import os
import json
from datetime import datetime
from airflow.operators.python import task
from google.cloud import storage

def transform_logic(raw_data):
    """
    This function should add "transformation_timestamp" and "data_interval_start" fields to all records.
    """
    transformed_data = []

    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_interval_start =  current_timestamp

    for record in raw_data:
        record['transformation_timestamp'] = current_timestamp
        record['data_interval_start'] = data_interval_start
        transformed_data.append(record)

    return transformed_data

def save_to_gcs(data, gcs_bucket, gcs_path):
    client = storage.Client()
    bucket = client.get_bucket(gcs_bucket)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f'airports_{timestamp}.json'
    blob = bucket.blob(os.path.join(gcs_path, file_name))

    with blob.open("w") as f:
         # Save data to GCS
        json.dump(data, f)

    return file_name


def transform_data(gcs_bucket, gcs_path, **kwargs):
    client = storage.Client()
    bucket = client.get_bucket(gcs_bucket)
    blob = bucket.blob(gcs_path)

    # Load raw data from GCS
    raw_data = json.loads(blob.download_as_string())

    # Perform transformation
    transformed_data = transform_logic(raw_data)

    # Save transformed data to GCS
    transformed_gcs_path = save_to_gcs(transformed_data, gcs_bucket, 'staged_data')
    return transformed_gcs_path
