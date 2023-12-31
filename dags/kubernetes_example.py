from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from kubernetes.client import models as k8s
# from airflow_utils import pod_env_vars, DBT_IMAGE


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.utcnow(),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    # "retry_delay": timedelta(minutes=5),
}

dag = DAG("kubernetes_sample", default_args=default_args, schedule_interval="*/2 * * * *",)


start = DummyOperator(task_id="run_this_first", dag=dag)

# intentionally pointing to "default" kubernetes namespace to illustrate that pods can run in different environments
# "default" should work for cloud composer as well
passing_python = KubernetesPodOperator(
    namespace="airflow",
    image="python:3.7-slim",
    cmds=["python", "-c"],
    arguments=["print('hello world')"],
    labels={"foo": "bar"},
    name="passing-python",
    task_id="passing-python-task",
    get_logs=True,
    dag=dag,
)

passing_bash = KubernetesPodOperator(
    namespace="airflow",
    image="ubuntu:16.04",
    cmds=["/bin/bash", "-cx"],
    arguments=["echo hello world"],
    labels={"foo": "bar"},
    name="fail",
    task_id="passing-bash-task",
    get_logs=True,
    dag=dag,
)

private_gcr_passing = KubernetesPodOperator(
    namespace="airflow",
    image="docker.io/hungnp1994/dbt_docker:v1",
    image_pull_secrets=[k8s.V1LocalObjectReference('dbt-docker-alpha')],
    cmds=["python", "-c"],
    arguments=["print('hello world')"],
    labels={"foo": "bar"},
    name="private-gcr-passing",
    task_id="private-gcr-passing-task",
    get_logs=True,
    # Storing sensitive credentials in env_vars will be exposed in plain text
    dag=dag,
)

start >> [passing_python, passing_bash, private_gcr_passing]