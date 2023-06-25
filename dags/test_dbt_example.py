from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from kubernetes.client import models as k8s

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 1),
    'retries': 7,
    'retry_delay': timedelta(minutes=5),
    # KubernetesPodOperator Defaults
    'namespace': 'airflow',
    'in_cluster': True,  # if set to true, will look in the cluster, if false, looks for file
    'get_logs': True,
    'is_delete_operator_pod': True
}

dag = DAG('Dbt-Airflow',
          default_args=default_args,
          description='Kubernetes Pod Operator - Demonstration Dag',
          schedule_interval='*/2 * * * *',
          start_date=datetime(2023, 6, 23),
          catchup=False)

start = DummyOperator(task_id="run_this_first", dag=dag)

migrate_data = KubernetesPodOperator(
        namespace='airflow',
        image='us-central1-docker.pkg.dev/sawyer-work-1804/airflow-dbt-gke/dbt-transformations:latest',
        image_pull_secrets=[k8s.V1LocalObjectReference('airflow-dbt-art')],
        cmds=["dbt", "run"],
        arguments=[
            "--project-dir", "./dbt_project_4", "--profiles-dir", "./dbt_project_4/profiles"
        ],
        name="dbt_transformations",
        task_id="dbt_transformations",
        get_logs=True,
        dag=dag
    )

docker_host_container = KubernetesPodOperator(
        namespace='airflow',
        image='docker.io/hungnp1994/dbt-transformations:latest',
        image_pull_secrets=[k8s.V1LocalObjectReference('dbt-docker-alpha')],
        cmds=["dbt", "run"],
        arguments=[
            "--project-dir", "./dbt_project_4", "--profiles-dir", "./dbt_project_4/profiles"
        ],
        name="dbt_transformations",
        task_id="dbt_transformations_with_docker_host",
        get_logs=True,
        dag=dag
    )

start >> [docker_host_container, migrate_data]

