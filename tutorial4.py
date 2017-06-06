
# -*- coding: utf-8 -*-
# BigQueryからデータを読み込み
# データを加工して
# BigQueryに書き込む
# +----------------+
# |                |
# | Read BigQuery  |
# |                |
# +-------+--------+
#         |
#         v
# +-------+--------+
# |                |
# | Modify Element |
# |                |
# +----------------+
#         |
#         v
# +-------+--------+
# |                |
# | Write BigQuery |
# |                |
# +----------------+

import apache_beam as beam

# Dataflowの基本設定
# ジョブ名、プロジェクト名、一時ファイルの置き場を指定します。
options = beam.options.pipeline_options.PipelineOptions()
gcloud_options = options.view_as(
    beam.options.pipeline_options.GoogleCloudOptions)
gcloud_options.job_name = 'dataflow-tutorial4'
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


def modify_data1(element):
    # beam.Mapは１行の入力に対し１行の出力をする場合に使う
    # element = {u'corpus_date': 0, u'corpus': u'sonnets', u'word': u'LVII', u'word_count': 1}

    corpus_upper = element['corpus'].upper()
    word_len = len(element['word'])

    return {'corpus_upper': corpus_upper,
            'word_len': word_len
            }


p4 = beam.Pipeline(options=options)

query = 'SELECT * FROM [bigquery-public-data:samples.shakespeare] LIMIT 10'
(p4 | 'read' >> beam.io.Read(beam.io.BigQuerySource(project='PROJECTID', use_standard_sql=False, query=query))
    | 'modify' >> beam.Map(modify_data1)
    | 'write' >> beam.io.Write(beam.io.BigQuerySink(
        'testdataset.testtable2',
        schema='corpus_upper:STRING, word_len:INTEGER',
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))
 )

p4.run()  # .wait_until_finish()
