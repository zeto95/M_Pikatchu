import json
import os
import requests
from datetime import datetime
from airflow.operators.python import task
from airflow.hooks.base import BaseHook
from google.cloud import storage
from configparser import ConfigParser

# Configuring GCS connection in airflow
GCS_CONN_ID = "gcs_connection"

# Getting the API key from the config.ini, better to be saved in an airflow varaible 
config_file_path = './config/config.ini'
config = ConfigParser()
config.read(config_file_path)
api_key = config["api"]["key"]
target_country = config["api"]["country"]

def extract_data(gcs_bucket, gcs_path):
    """
    Extract data from an API and save it to Google Cloud Storage (GCS).

    :param gcs_bucket: The GCS bucket to store the data.
    :param gcs_path: The path within the GCS bucket to save the file.
    """
    # Retrieve GCS connection details
    gcs_conn = BaseHook.get_connection(GCS_CONN_ID)
    
    # Set up GCS client
    client = storage.Client.from_service_account_info(gcs_conn.extra_dejson)
    bucket = client.get_bucket(gcs_bucket)

    url = 'https://api.api-ninjas.com/v1/airports?name={}'.format(target_country)

    try:
        response = requests.get(url, headers={'X-Api-Key': api_key})
        response.raise_for_status()

        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            file_name = save_to_gcs(data, bucket, gcs_path)
            xcom_push(context, key="gcs_path", value=os.path.join(gcs_path, file_name))
        else:
            print(f"Error during extraction: Non-JSON response received. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during extraction: {e}")
        return None

def save_to_gcs(data, bucket, gcs_path):
    """
    Save data to GCS.

    :param data: The data to be saved.
    :param bucket: The GCS bucket.
    :param gcs_path: The path within the GCS bucket to save the file.
    :return: The file name.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f'{target_country.lower()}_airports_{timestamp}.json'
    blob = bucket.blob(os.path.join(gcs_path, file_name))

    with blob.open("w") as f:
        json.dump(data, f)

    return file_name
