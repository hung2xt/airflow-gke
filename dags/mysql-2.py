from multiprocessing import connection
from airflow import DAG
from airflow.decorators import task
import mysql.connector
import pandas as pd
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from datetime import datetime, timedelta
import pyodbc
from airflow import XComArg
from airflow.utils.task_group import TaskGroup
from airflow.decorators import task


default_args = {
               'owner': 'user',
               'depends_on_past': False,
               'start_date': datetime(2022, 9, 23),
               'email': ['hungnp@daplogistics.vn'],
               'email_on_failure': False,
               'email_on_retry': False,
               'retries': 1,
               'retry_delay': timedelta(minutes=1),
}
 

tables = ['F_SLA_DETAIL','SALE_ORDER_MINI']

def fin_conn(table = 'F_SLA_DETAIL'):
    mydb = mysql.connector.connect(host="103.9.158.8", user="dpl_business_intelligence", password="asd@1234A", database = 'DPL_BUSINESS_INTELLIGENCE')
    mycursor = mydb.cursor()

    mycursor.execute(f"""SELECT * FROM {table}""")

    myresult = mycursor.fetchall()

    df = pd.DataFrame(data=myresult, columns=[x[0] for x in mycursor.description])

    return df.to_parquet(f'/Users/hungnp14/Desktop/Airflow/airflow-output/{table}.parquet', engine='pyarrow')

    mycursor.close()
    mydb.close()


with DAG(
   dag_id="parallel_dag_3",
   start_date=datetime.today() - timedelta(days=1),
   schedule_interval='*/6 * * * *',
   concurrency=100,
   default_args=default_args,
   catchup=False
) as dag:
    l1 = PythonOperator(task_id='task1', python_callable=fin_conn)