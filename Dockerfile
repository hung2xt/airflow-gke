FROM apache/airflow:2.4.1
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY dags $AIRFLOW_HOME/dags