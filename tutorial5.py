
# -*- coding: utf-8 -*-
# ブランチを分ける例
# +----------------+
# |                |
# | Read BigQuery  |
# |                |
# +-------+--------+
#         |
#         +---------------------+
#         |                     |
# +-------v--------+    +-------v--------+
# |                |    |                |
# | Modify Element |    | Modify Element |
# |                |    |                |
# +-------+--------+    +-------+--------+
#         |                     |
#         +---------------------+
#         |
# +-------v--------+
# |                |
# | Flatten        |
# |                |
# +-------+--------+
#         |
#         |
# +-------v--------+
# |                |
# | Save BigQuery  |
# |                |
# +----------------+

import apache_beam as beam

# Dataflowの基本設定
# ジョブ名、プロジェクト名、一時ファイルの置き場を指定します。
options = beam.options.pipeline_options.PipelineOptions()
gcloud_options = options.view_as(
    beam.options.pipeline_options.GoogleCloudOptions)
gcloud_options.job_name = 'dataflow-tutorial5'
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


def modify1(element):
    # element = {u'corpus_date': 0, u'corpus': u'sonnets', u'word': u'LVII', u'word_count': 1}
    word_count = len(element['corpus'])
    count_type = 'corpus only'

    return {'word_count': word_count,
            'count_type': count_type
            }


def modify2(element):
    # element = {u'corpus_date': 0, u'corpus': u'sonnets', u'word': u'LVII', u'word_count': 1}
    word_count = len(element['word'])
    count_type = 'word only'

    return {'word_count': word_count,
            'count_type': count_type
            }


p5 = beam.Pipeline(options=options)

query = 'SELECT * FROM [bigquery-public-data:samples.shakespeare] LIMIT 10'
query_results = p5 | 'read' >> beam.io.Read(beam.io.BigQuerySource(
    project='PROJECTID', use_standard_sql=False, query=query))

# BigQueryの結果を二つのブランチに渡す
branch1 = query_results | 'modify1' >> beam.Map(modify1)
branch2 = query_results | 'modify2' >> beam.Map(modify2)

# ブランチからの結果をFlattenでまとめる
((branch1, branch2) | beam.Flatten()
                    | 'write' >> beam.io.Write(beam.io.BigQuerySink(
                        'testdataset.testtable3',
                        schema='word_count:INTEGER, count_type:STRING',
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))
 )

p5.run()  # .wait_until_finish()
