
# -*- coding: utf-8 -*-
# Groupbyを使う

import apache_beam as beam

# Dataflowの基本設定
# ジョブ名、プロジェクト名、一時ファイルの置き場を指定します。
options = beam.options.pipeline_options.PipelineOptions()
gcloud_options = options.view_as(
    beam.options.pipeline_options.GoogleCloudOptions)
gcloud_options.job_name = 'dataflow-tutorial6'
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


def modify_data2(kvpair):
    # groupbyによりkeyとそのkeyを持つデータのリストのタプルが渡される
    # kvpair = (u'word only', [4, 4, 6, 6, 7, 7, 7, 7, 8, 9])

    return {'count_type': kvpair[0],
            'sum': sum(kvpair[1])
            }


p6 = beam.Pipeline(options=options)

query = 'SELECT * FROM [PROJECTID:testdataset.testtable3] LIMIT 20'
(p6 | 'read' >> beam.io.Read(beam.io.BigQuerySource(project='PROJECTID', use_standard_sql=False, query=query))
    | 'pair' >> beam.Map(lambda x: (x['count_type'], x['word_count']))
    | "groupby" >> beam.GroupByKey()
    | 'modify' >> beam.Map(modify_data2)
    | 'write' >> beam.io.Write(beam.io.BigQuerySink(
        'testdataset.testtable4',
        schema='count_type:STRING, sum:INTEGER',
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))
 )

p6.run()  # .wait_until_finish()
