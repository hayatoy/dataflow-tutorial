
# -*- coding: utf-8 -*-
# GCSからファイルを読み込み、GCSにその内容を書き込むだけ
# +----------------+
# |                |
# | Read GCS File  |
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
gcloud_options.job_name = 'dataflow-tutorial1'
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


p1 = beam.Pipeline(options=options)

(p1 | 'read' >> beam.io.ReadFromText('gs://dataflow-samples/shakespeare/kinglear.txt')
    | 'write' >> beam.io.WriteToText('gs://PROJECTID/test.txt', num_shards=1)
 )

p1.run()  # .wait_until_finish()
