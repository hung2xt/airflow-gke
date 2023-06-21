from airflow import DAG
from airflow.operators.bash import BashOperator
#from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta
#from airflow.providers.common.sql.operators.sql import SQLColumnCheckOperator, SQLTableCheckOperator,SQLColumnCheckOperator
#from airflow.operators.sql import SQLCheckOperator


with DAG(
    dag_id="query-mysql-local",
    start_date=datetime(2022,8,1),
    schedule_interval='*/10 * * * *',
    catchup=False
) as dag:

    # Use the node command to execute the JavaScript file from the command line
    QueryMysql = BashOperator(
        task_id="query-mysql-1",
        bash_command="python3 /Users/hungnp14/Desktop/python-3.8-virtualenv/airflow/scripts/mysql_py_test.py"
    )

    QueryHiveSpark = BashOperator(
        task_id = 'query-hive-spark',
        bash_command = "spark-submit --jars /Users/hungnp14/bigdata/spark-2.4.3-bin-hadoop2.7/jars/hive-exec-1.2.1.spark2.jar \
/Users/hungnp14/Desktop/python-3.8-virtualenv/airflow/scripts/hive-spark.py –files /Users/hungnp14/bigdata/hive-3.1.2-bin/conf/hive-site.xml"
    )

    SqoopImport = BashOperator(
        task_id = 'sqoop-hdfs',
        bash_command = "cd /Users/hungnp14/bigdata/sqoop-1.4.7.bin__hadoop-2.6.0/bin &&./sqoop import --connect jdbc:mysql://localhost:3306/classicmodels --username root \
          --password asd@1234 --table employees --m 1 --delete-target-dir --target-dir /sqoop_import_to_hdfs/employees")

    SqoopTruncate = BashOperator(
        task_id = 'sqoop-hdfs-to-mysql-truncate',
        bash_command = "cd /Users/hungnp14/bigdata/sqoop-1.4.7.bin__hadoop-2.6.0/bin &&./sqoop eval --connect jdbc:mysql://localhost:3306/classicmodels \
                       --username root --password asd@1234 --query 'TRUNCATE TABLE employees_hdfs'")

    SqoopExport = BashOperator(
        task_id = 'sqoop-hdfs-to-mysql',
        bash_command = "cd /Users/hungnp14/bigdata/sqoop-1.4.7.bin__hadoop-2.6.0/bin &&./sqoop export --connect jdbc:mysql://localhost:3306/classicmodels \
                       --username root --password asd@1234 --table employees_hdfs  --export-dir /sqoop_import_to_hdfs/employees"
    )
    
#     SparkSubmitExtract = SparkSubmitOperator(
# 		application ='/Users/hungnp14/Desktop/python-3.8-virtualenv/airflow/scripts/SparkMysql.py',
# 		conn_id= 'spark_default', 
# 		task_id='spark_submit_task'
# 		)
    
#     SparkSubmitSQLServer = SparkSubmitOperator(
# 		application ='/Users/hungnp14/Desktop/python-3.8-virtualenv/airflow/scripts/SparkSQLServer.py',
# 		conn_id= 'spark_default', 
# 		task_id='spark_submit_task_sqlserver'
# 		)

#     table_checks = SQLTableCheckOperator(task_id="table_checks",
#     conn_id="mysql_conn",
#     table="payments",
#     partition_clause="paymentDate >= '2003-10-28'",
#     checks={
#         "my_row_count_check": {
#             "check_statement": "COUNT(*) >= 270"
#             }
#     }
# )
#     payments_row_quality_check = SQLCheckOperator(
#     conn_id="mysql_conn",
#     task_id="payments_row_quality_check",
#     sql="payments_sql.sql",
#     params={"paymentDate": "2004-12-15"},
# )

#     table_checks_agg = SQLTableCheckOperator(
#     task_id="table_checks_agg",
#     conn_id="mysql_conn",
#     table="products",
#     #partition_clause="START_DATE >= '2022-01-01'"
#     checks={
#         "my_row_count_check": {
#             "check_statement": "COUNT(*) >= 10"
#             },
#         "my_column_sum_comparison_check": {
#             "check_statement": "SUM(MY_COL_1) < SUM(MY_COL_2)",
#             "partition_clause": "MY_COL_4 > 100"
#             },
#         "my_column_addition_check": {
#             "check_statement": "MY_COL_1 + MY_COL_2 = MY_COL_3"
#             }
#     }
# )
    dbtBigquery = BashOperator(
        task_id = 'dbt-airflow-bg',
        bash_command = "cd /Users/hungnp14/Desktop/dbt-project/dbt-google-bigquery/dbt_gbq && dbt debug && dbt run"
    )

    # Use the Rscript command to execute the R file which is being provided
    # with the result from task one via an environment variable via XComs
    # print_ISS_coordinates = BashOperator(
    #     task_id="print_ISS_coordinates",
    #     bash_command="Rscript $AIRFLOW_HOME/include/my_R_script.R $ISS_COORDINATES",
    #     env={
    #         "ISS_COORDINATES": "{{ task_instance.xcom_pull(\
    #                            task_ids='get_ISS_coordinates', \
    #                            key='return_value') }}"
    #     },
    #     # set append_env to True to be able to use env variables
    #     # like AIRFLOW_HOME from the Airflow environment
    #     append_env=True
    # )

    QueryMysql

    #https://docs.astronomer.io/learn/data-quality