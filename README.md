# Airport ETL Project Readme

## Overview
This project is an Extract, Transform, Load (ETL) pipeline designed to collect and process data related to airports in a specific country. The ETL process is implemented using Apache Airflow, Google Cloud Storage (GCS), and an external API.

## Project Structure

- `dags/`: Contains the Airflow DAG script (`airport_etl_dag.py`) responsible for orchestrating the ETL process.
- `config/`: Includes the configuration files for API keys (`config.ini`).


## Disclaimer
In this project, the `transform.py` and `extract.py` scripts are placed directly in the `dags/` directory for simplicity. However, this practice is not recommended for production environments, and it is advisable to separate DAGs and scripts for better organization. In production Airflow should not be used to perform the ETL process, however to orchestrate it.
Also, while running the project locally, scripts and dags were in different directories as well as the output files of the `raw_data` and `staged_data` 

## Docker and Airflow Configuration
The project utilizes Docker to set up the development environment. Airflow is configured within a Docker image, making it easy to deploy and run the ETL process consistently across environments.

## GCS Buckets Configuration
Google Cloud Storage (GCS) is used for storing both raw and staged data. The buckets used are:
- `airports_raw_data`: Stores raw data extracted from the API.
- `airports_staged_data`: Stores transformed data after processing.

## Configuration Files
- `config.ini`: Configuration file holding API keys and country name 'German'. Adding the country in the config file was to avoid any hard-coded values in the code and to be more scalable for future usage. Also, it would be better to save both as variables in Airflow and retrieve them. 
- `airflow.cfg`: Airflow configuration file (within the docker image)

## Service Account in GCP
To interact with GCS, a service account was created in Google Cloud Platform (GCP). This service account is associated with the `gcs-connection` in Airflow for secure access to GCS buckets.

## Local Development
The project was initially developed and tested locally. The extract process successfully fetched data from the API, and the transform process created an error-free Json response.

## Authentication Error
During the transition to GCP, an authentication error was encountered. This was resolved by setting up Application Default Credentials (ADC) and ensuring that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable was correctly configured.

## XCom Usage
Airflow XCom is utilized to pass the GCS path from the extract to the transform task within the DAG. This allows seamless data transfer between tasks in the workflow.

## Transformation Logic
The `transform_logic` function in the `transform.py` script adds two fields, `transformation_timestamp` and `data_interval_start`, to each record in the dataset.

## Additional Field - `data_interval_start`
The purpose of the `data_interval_start` field was not initially clear. To enhance clarity, the current timestamp was added to this field, representing the time when the ETL job was run.

## Regarding the Load_data operator 

Here's an example using the `GoogleCloudStorageToBigQueryOperator`: This operator simplifies the process and avoids the need for an intermediate step.

```python
from airflow.providers.google.transfers.gcs_to_bigquery import GoogleCloudStorageToBigQueryOperator
from datetime import datetime, timedelta

load_to_bigquery_task = GoogleCloudStorageToBigQueryOperator(
    task_id='load_to_bigquery',
    bucket_name=gcs_bucket,
    source_objects=[f'{gcs_prefix}/{{ ds_nodash }}/*.json'],
    destination_project_dataset_table=f'{destination_project}.{destination_dataset}.{table_name}',
    schema_fields=[...],  # Define your schema fields
    write_disposition='WRITE_APPEND',
    create_disposition='CREATE_IF_NEEDED',
    autodetect=True,
    skip_leading_rows=1,
    allow_quoted_newlines=True,
    source_format='NEWLINE_DELIMITED_JSON',
    bigquery_conn_id='bigquery_default',  # Connection ID configured in Airflow
    google_cloud_storage_conn_id='google_cloud_storage_default',  # Connection ID configured in Airflow
    dag=dag
)
```

Also, there is two more ways and operators that could be used:
1. Using BigQuery Operator
from airflow.providers.google.transfers.gcs_to_bigquery import GCSToBigQueryOperator

2. Using BigQueryHook 



