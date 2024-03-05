from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from extract import extract_data
from transform import transform_data

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=8),
}

@dag(
    'airport_etl_dag',
    schedule_interval=timedelta(days=1),
    default_args=default_args,
    catchup=False,
    description='ETL DAG for country airports data',
)
def airport_etl_dag():

    @task
    def extract_task(gcs_conn_id='gcs_connection'):
        gcs_hook = BaseHook.get_connection(gcs_conn_id)
        return extract_data(gcs_bucket='airports_raw_data',
                             gcs_path='your_gcs_path')

    @task
    def transform_task(data, gcs_conn_id='gcs_connection'):
        gcs_hook = BaseHook.get_connection(gcs_conn_id)
        return transform_data(data,
                              gcs_bucket='airports_staged_data',
                              gcs_path='your_gcs_path')

    
    @task
    def load():
        # Please check the readme.txt file to check suggestion and example about the load operator 
        print("Loading data into the destination")

    extract_task_instance = extract_task()
    transform_task_instance = transform_task(extract_task_instance)
    load_task = load()

    extract_task_instance >> transform_task_instance >> load_task


airport_etl_dag_instance = airport_etl_dag()
