from airflow import DAG

from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
import boto3

aws_access_key_id = Variable.get('aws_access_key_id')
aws_secret_access_key = Variable.get('aws_secret_access_key')
glue = boto3.client('glue', region_name='us-east-1',
                    aws_access_key_id=aws_access_key_id, 
                    aws_secret_access_key=aws_secret_access_key)

from airflow.utils.dates import days_ago


def trigger_crawler_enem2020_microdados_func():
    glue.start_crawler(Name='enem2020_crawler_microdados')

with DAG(
    'desafio_final_edc_enem_2020',
    default_args={
        'owner': 'Claudio',
        'depends_on_past': False,
        'email': ['claudiopinho@yahoo.com.br'],
        'email_on_failure': False,
        'email_on_retry': False,
        'max_active_runs': 1,
    },
    description='Extração e processamento de dados do ENEM 2020',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['spark', 'kubernetes', 'batch', 'ENEM'],
) as dag:

    # extracao = KubernetesPodOperator(
    #     namespace='airflow',
    #     image="539445819060.dkr.ecr.us-east-1.amazonaws.com/extraction-edsup-2019:latest",
    #     cmds=["python", "/run.py"],
    #     name="extraction-edsup-2019",
    #     task_id="extraction-edsup-2019",
    #     image_pull_policy="Always",
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     get_logs=True,
    # )

    inicio = DummyOperator(task_id='inicio')

    converte_MICRODADOS_parquet = SparkKubernetesOperator(
        task_id='converte_MICRODADOS_parquet',
        namespace="airflow",
        application_file="dag_enem2020_converte_MICRODADOS_parquet.yaml",
        kubernetes_conn_id="kubernetes_default",
        do_xcom_push=True,
    )

    converte_MICRODADOS_parquet_monitor = SparkKubernetesSensor(
        task_id='converte_MICRODADOS_parquet_monitor',
        namespace="airflow",
        application_name="{{ task_instance.xcom_pull(task_ids='converte_MICRODADOS_parquet')['metadata']['name'] }}",
        kubernetes_conn_id="kubernetes_default",
    )

    trigger_crawler_enem2020_microdados = PythonOperator(
        task_id='trigger_crawler_enem2020_MICRODADOS',
        python_callable=trigger_crawler_enem2020_microdados_func,
    )

inicio >> [converte_MICRODADOS_parquet]
converte_MICRODADOS_parquet_monitor >> trigger_crawler_enem2020_microdados
