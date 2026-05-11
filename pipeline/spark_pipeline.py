"""Conflict Analysis PySpark Pipeline — Azure Databricks."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os


def get_spark():
    return SparkSession.builder.appName("ConflictAnalysisPipeline").getOrCreate()


def compute_incident_trends(incidents_df):
    return (
        incidents_df
        .withColumn("month", F.trunc("date", "month"))
        .groupBy("state", "conflict_type", "month")
        .agg(
            F.count("*").alias("incident_count"),
            F.sum("fatalities").alias("total_fatalities"),
            F.sum("displaced").alias("total_displaced"),
            F.avg("fatalities").alias("avg_fatalities_per_incident"),
        )
        .withColumn("intensity_score",
                    F.col("incident_count") * 0.4 + F.col("total_fatalities") * 0.6)
    )


def identify_hotspot_states(incidents_df, top_n: int = 10):
    return (
        incidents_df
        .groupBy("state", "lat", "lon")
        .agg(
            F.count("*").alias("total_incidents"),
            F.sum("fatalities").alias("total_fatalities"),
            F.sum("displaced").alias("total_displaced"),
        )
        .orderBy(F.col("total_incidents").desc())
        .limit(top_n)
    )


def compute_actor_network(incidents_df):
    return (
        incidents_df
        .groupBy("actor1", "actor2")
        .agg(F.count("*").alias("clash_count"),
             F.sum("fatalities").alias("total_fatalities"))
        .orderBy(F.col("clash_count").desc())
    )


if __name__ == "__main__":
    spark = get_spark()
    incidents = spark.read.csv("data/incidents.csv", header=True, inferSchema=True)
    trends = compute_incident_trends(incidents)
    trends.show(10)
    hotspots = identify_hotspot_states(incidents)
    hotspots.show(10)
    actor_net = compute_actor_network(incidents)
    actor_net.show(10)
    spark.stop()
