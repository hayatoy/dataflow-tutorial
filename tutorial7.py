
# -*- coding: utf-8 -*-
# WindowでGroupByの区間を区切る

import apache_beam as beam

# Dataflowの基本設定
# ジョブ名、プロジェクト名、一時ファイルの置き場を指定します。
options = beam.options.pipeline_options.PipelineOptions()
gcloud_options = options.view_as(
    beam.options.pipeline_options.GoogleCloudOptions)
gcloud_options.job_name = 'dataflow-tutorial7'
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


def assign_timevalue(v):
    # pcollectionのデータにタイムスタンプを付加する
    # 後段のwindowはこのタイムスタンプを基準に分割される
    # ここでは適当に乱数でタイムスタンプを入れている
    import apache_beam.transforms.window as window
    import random
    import time
    return window.TimestampedValue(v, int(time.time()) + random.randint(0, 1))


def modify_data3(kvpair):
    # groupbyによりkeyとそのkeyを持つデータのリストのタプルが渡される
    # windowで分割されているのでデータ数が少なくなる
    # kvpair = (u'word only', [4, 4, 6, 6, 7])

    return {'count_type': kvpair[0],
            'sum': sum(kvpair[1])
            }


p7 = beam.Pipeline(options=options)

query = 'SELECT * FROM [PROJECTID:testdataset.testtable3] LIMIT 20'
(p7 | 'read' >> beam.io.Read(beam.io.BigQuerySource(project='PROJECTID', use_standard_sql=False, query=query))
    | "assign tv" >> beam.Map(assign_timevalue)
    | 'window' >> beam.WindowInto(beam.window.FixedWindows(1))
    | 'pair' >> beam.Map(lambda x: (x['count_type'], x['word_count']))
    | "groupby" >> beam.GroupByKey()
    | 'modify' >> beam.Map(modify_data3)
    | 'write' >> beam.io.Write(beam.io.BigQuerySink(
        'testdataset.testtable5',
        schema='count_type:STRING, sum:INTEGER',
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))
 )

p7.run()  # .wait_until_finish()
