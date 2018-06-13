import logging

from airflow.hooks.postgres_hook import PostgresHook
from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

log = logging.getLogger(__name__)

class S3ToRedshiftOperator(BaseOperator):

  @apply_defaults
  def __init__(self, redshift_conn_id,table,s3_bucket,s3_path,s3_access_key_id,
    s3_secret_access_key,delimiter,region,*args, **kwargs):

    self.redshift_conn_id = redshift_conn_id
    self.table = table
    self.s3_bucket = s3_bucket
    self.s3_path = s3_path
    self.s3_access_key_id = s3_access_key_id
    self.s3_secret_access_key = s3_secret_access_key
    self.delimiter = delimiter
    self.region = region

    super(S3ToRedshiftOperator, self).__init__(*args, **kwargs)


  def execute(self, context):
    self.hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)
    conn = self.hook.get_conn()
    cursor = conn.cursor()
#    log.info("Connected with " + self.redshift_conn_id)

    load_statement = """
      copy
      {0}
      from 's3://{1}/{2}'
      access_key_id '{3}' secret_access_key '{4}'
      delimiter '{5}' region '{6}' """.format(
    self.table, self.s3_bucket, self.s3_path,
    self.s3_access_key_id, self.s3_secret_access_key,
    self.delimiter, self.region)
    cursor.execute(load_statement)
    cursor.close()
    conn.commit()
#    log.info("Load command completed")

    return True


class S3ToRedshiftOperatorPlugin(AirflowPlugin):
  name = "redshift_load_plugin"
  operators = [S3ToRedshiftOperator]
