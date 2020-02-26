import os

from pyspark.shell import spark, sc, sqlContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils, TopicAndPartition
import json
import time

os.environ['SPARK_HOME'] = "/user/spark"

START = 0
PARTITION = 0
TOPIC = "dim_products"
BROKER_LIST = 'cdh631.itfbgroup.local:9092'
HDFS_OUTPUT_PATH = "hdfs://cdh631.itfbgroup.local:8020/user/usertest/okko/dim_products"

HOST_IP = "192.168.88.95"
PORT = "1521"
SID = "orcl"

TARGET_DB_TABLE_NAME = "DIM_PRODUCTS"
TARGET_DB_USER_NAME = "test_user"
TARGET_DB_USER_PASSWORD = "test_user"


def parse(line):
    data = json.loads(line)
    return data['product_id'], data['category_id'], data['category_code'], data['brand'], data['description'], data[
        'name'], data['price'], data['last_update_date']


def deserializer():
    return bytes.decode


def save_data(rdd):
    if not rdd.isEmpty():
        rdd = rdd.map(lambda m: parse(m[1]))
        df = sqlContext.createDataFrame(rdd)
        df.createOrReplaceTempView("t")
        result = spark.sql(
            "select _1 as product_id,_2 as category_id,_3 as category_code,_4 as brand,_5 as description,_6 as name,_7 as price,to_timestamp(_8) as last_update_date from t")

        # Writing to HDFS
        result.write \
            .format("csv") \
            .mode("append") \
            .option("header", "true") \
            .save(HDFS_OUTPUT_PATH)

        # Writing to Oracle DB
        result.write \
            .format("jdbc") \
            .mode("append") \
            .option("driver", 'oracle.jdbc.OracleDriver') \
            .option("url", "jdbc:oracle:thin:@{0}:{1}:{2}".format(HOST_IP, PORT, SID)) \
            .option("dbtable", TARGET_DB_TABLE_NAME) \
            .option("user", TARGET_DB_USER_NAME) \
            .option("password", TARGET_DB_USER_PASSWORD) \
            .save()
    else:
        ssc.stop()
    return rdd


def storeOffsetRanges(rdd):
    global offsetRanges
    offsetRanges = rdd.offsetRanges()
    return rdd


def printOffsetRanges(rdd):
    for o in offsetRanges:
        f = open('offset_value_dim_products.txt', 'w')
        f.write(str(o.untilOffset))
        f.close()


if __name__ == "__main__":
    ssc = StreamingContext(sc, 5)
    topicPartion = TopicAndPartition(TOPIC, PARTITION)
    f = open('offset_value_dim_products.txt', 'r')
    start = int(f.read())
    f.close()
    fromOffset = {topicPartion: start}
    kafkaParams = {"metadata.broker.list": BROKER_LIST}
    kafkaParams["enable.auto.commit"] = "false"

    directKafkaStream = KafkaUtils.createDirectStream(ssc, [TOPIC], kafkaParams, fromOffsets=fromOffset,
                                                      keyDecoder=deserializer(), valueDecoder=deserializer())

    time.sleep(5)
    directKafkaStream.foreachRDD(lambda x: save_data(x))
    directKafkaStream.transform(storeOffsetRanges) \
        .foreachRDD(printOffsetRanges)

    ssc.start()
    ssc.awaitTermination()
