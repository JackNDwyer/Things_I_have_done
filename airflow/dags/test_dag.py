import datetime as dt
from airflow import DAG

import airflow.operators.redshift_upsert_plugin as pack1
import airflow.operators.redshift_load_plugin as pack2 
default_args = {
  'owner': 'me',
  'start_date': dt.datetime(2017, 6, 1),
  'retries': 2,
  'retry_delay': dt.timedelta(minutes=5),
}
 
dag = DAG('redshift-demo',
  default_args=default_args,
  schedule_interval='@once'
)

upsert = pack1.RedshiftUpsertOperator(
  task_id='upsert',
  src_redshift_conn_id="ps_1",
  dest_redshift_conn_id="ps_1",
  src_table="airflow1",
  dest_table="airflow2",
  src_keys=["id"],
  dest_keys=["id"],
  dag = dag
)
 
load = pack2.S3ToRedshiftOperator(
  task_id="load",
  redshift_conn_id="ps_1",
  table="airflow1",
  s3_bucket="test-blast",
  s3_path="test.csv",
  s3_access_key_id="AKIAJBJH6KZPBW6CQL3A",
  s3_secret_access_key="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",
  delimiter=",",
  region="us-west-2",
  dag=dag
)
 
load >> upsert
