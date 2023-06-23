FROM apache/airflow

COPY ./dags/ \${AIRFLOW_HOME}/dags/
COPY ./plugins/ \${AIRFLOW_HOME}/plugins/

COPY requirements.txt .
RUN pip install -r requirements.txt