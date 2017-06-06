
# -*- coding: utf-8 -*-
# BigQueryからデータを読み込み、GCSにその内容を書き込むだけ
# BigQueryのデータセットは以下
# https://bigquery.cloud.google.com/table/bigquery-public-data:samples.shakespeare
# +----------------+
# |                |
# | Read BigQuery  |
# |                |
# +-------+--------+
#         |
#         v
# +-------+--------+
# |                |
# | Write GCS File |
# |                |
# +----------------+

import apache_beam as beam

# Dataflowの基本設定
# ジョブ名、プロジェクト名、一時ファイルの置き場を指定します。
options = beam.options.pipeline_options.PipelineOptions()
gcloud_options = options.view_as(
    beam.options.pipeline_options.GoogleCloudOptions)
gcloud_options.job_name = 'dataflow-tutorial2'
gcloud_options.project = 'PROJECTID'
gcloud_options.staging_location = 'gs://PROJECTID/staging'
gcloud_options.temp_location = 'gs://PROJECTID/temp'


# Dataflowのスケール設定
# Workerの最大数や、マシンタイプ等を設定します。
# WorkerのDiskサイズはデフォルトで250GB(Batch)、420GB(Streaming)と大きいので、
# ここで必要サイズを指定する事をオススメします。
worker_options = options.view_as(beam.options.pipeline_options.WorkerOptions)
worker_options.disk_size_gb = 20
worker_options.max_num_workers = 2
# worker_options.num_workers = 2
# worker_options.machine_type = 'n1-standard-8'


# 実行環境の切り替え
# DirectRunner: ローカルマシンで実行します
# DataflowRunner: Dataflow上で実行します
# options.view_as(beam.options.pipeline_options.StandardOptions).runner = 'DirectRunner'
options.view_as(beam.options.pipeline_options.StandardOptions).runner = 'DataflowRunner'


p2 = beam.Pipeline(options=options)

query = 'SELECT * FROM [bigquery-public-data:samples.shakespeare] LIMIT 10'
(p2 | 'read' >> beam.io.Read(beam.io.BigQuerySource(project='PROJECTID', use_standard_sql=False, query=query))
    | 'write' >> beam.io.WriteToText('gs://PROJECTID/test2.txt', num_shards=1)
 )

p2.run()  # .wait_until_finish()
