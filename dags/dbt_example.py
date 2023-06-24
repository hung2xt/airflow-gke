from airflow import DAG
from datetime import datetime
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
# from kube_secrets import DBT_SERVICE_ACCOUNT, GIT_SECRET_ID_RSA_PRIVATE
# from airflow_utils import kube_pod_defaults, dbt_setup_cmds, DBT_IMAGE
from kubernetes.client import models as k8s

PROJECT_ID = "sawyer-work-1804"
pod_env_vars = {"PROJECT_ID": PROJECT_ID}

DBT_IMAGE = "docker.io/hungnp1994/dbt_docker:v1"
GIT_REPO = "https://github.com/hung2xt/airflow-gke.git"
GIT_BRANCH = "main"

git_clone_cmds = f"""
    /entrypoint.sh &&
    gcloud auth activate-service-account --key-file=account.json &&
    git clone {GIT_REPO} --project={PROJECT_ID}"""

dbt_setup_cmds = f"""
    {git_clone_cmds} &&
    cd {GIT_REPO}/dbt_bigquery_example &&
    git checkout {GIT_BRANCH} &&
    export PROJECT_ID={PROJECT_ID} &&
    export DBT_PROFILES_DIR=$(pwd) &&
    export DBT_GOOGLE_BIGQUERY_KEYFILE=/dbt/account.json"""

pod_env_vars = {**pod_env_vars, **{}}

default_args = {
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,  
    "email_on_retry": False,
    "email_on_success": False,
    "owner": "airflow",
    "retries": 0,
    "start_date": "2020-01-16 00:00:00",
}

dbt_debug_cmd = f"""
    {dbt_setup_cmds} &&
    dbt debug --target service_account_runs
"""

dbt_seed_cmd = f"""
    {dbt_setup_cmds} &&
    dbt seed --full-refresh --show --target service_account_runs
"""

dbt_run_cmd = f"""
    {dbt_setup_cmds} &&
    dbt run --target service_account_runs
"""

dbt_test_cmd = f"""
    {dbt_setup_cmds} &&
    dbt test --target service_account_runs
"""

with DAG("dbt_example", default_args=default_args, schedule_interval="@once") as dag:

    dbt_debug = KubernetesPodOperator(
        namespace="airflow",
        image=DBT_IMAGE,
        image_pull_secrets=[k8s.V1LocalObjectReference('dbt-docker-alpha')],
        task_id="dbt-debug",
        name="dbt-debug",
        arguments=[dbt_debug_cmd],
        # Storing sensitive credentials in env_vars will be exposed in plain text
        env_vars=pod_env_vars,
    )

    dbt_seed = KubernetesPodOperator(
        namespace="airflow",
        image=DBT_IMAGE,
        image_pull_secrets=[k8s.V1LocalObjectReference('dbt-docker-alpha')],
        task_id="dbt-seed",
        name="dbt-seed",
        arguments=[dbt_seed_cmd],
        # Storing sensitive credentials in env_vars will be exposed in plain text
        env_vars=pod_env_vars,
    )

    dbt_run = KubernetesPodOperator(
        namespace="airflow",
        image=DBT_IMAGE,
        image_pull_secrets=[k8s.V1LocalObjectReference('dbt-docker-alpha')],
        task_id="dbt-run",
        name="dbt-run",
        arguments=[dbt_run_cmd],
        # Storing sensitive credentials in env_vars will be exposed in plain text
        env_vars=pod_env_vars,
    )

    dbt_test = KubernetesPodOperator(
        namespace="airflow",
        image=DBT_IMAGE,
        image_pull_secrets=[k8s.V1LocalObjectReference('dbt-docker-alpha')],
        task_id="dbt-test",
        name="dbt-test",
        arguments=[dbt_test_cmd],
        # Storing sensitive credentials in env_vars will be exposed in plain text
        env_vars=pod_env_vars,
    )

    dbt_debug >> dbt_seed >> dbt_run >> dbt_test