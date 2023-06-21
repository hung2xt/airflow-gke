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
 
server = '113.190.255.74,49719\MISASME2022'
database = 'DPL_2020_2022'
username = 'DPL_getData'
password = 'G3tD@ta_DPL'
tables = ['F_SLA_DETAIL','SALE_ORDER_MINI']

def mysql_conn(table = None):
    mydb = mysql.connector.connect(host="127.0.0.1", user="root", password="asd@1234", database = 'classicmodels')
    mycursor = mydb.cursor()

    mycursor.execute(f"""SELECT * FROM payments""")

    myresult = mycursor.fetchall()

    df = pd.DataFrame(data=myresult, columns=[x[0] for x in mycursor.description])

    return df.to_parquet(f'/Users/hungnp14/Desktop/Airflow/airflow-output/{table}.parquet', engine='pyarrow')

    mycursor.close()
    mydb.close()


with DAG(
   dag_id="finance-mysql-conn",
   start_date=datetime.today() - timedelta(days=1),
   schedule_interval='*/3 * * * *',
   concurrency=100,
   default_args=default_args
) as dag:
   mysql_conn = PythonOperator(task_id='mysql_conn', python_callable=mysql_conn)