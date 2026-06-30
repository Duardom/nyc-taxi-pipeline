from prefect import flow, task
from google.cloud import storage, bigquery

@task
def subir_a_gcs():
    cliente = storage.Client(project='project-13385eff-5d97-4173-81d')
    bucket = cliente.bucket('nyc-taxi-pipeline-tu-nombre-jorge-gomez')
    blob = bucket.blob('raw/fhv_tripdata_2023-01.parquet')
    blob.upload_from_filename('fhv_tripdata_2023-01.parquet')
    print("Archivo subido a GCS")

@task
def cargar_a_bigquery():
    cliente_bq = bigquery.Client(project='project-13385eff-5d97-4173-81d')
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    uri = "gs://nyc-taxi-pipeline-tu-nombre-jorge-gomez/raw/fhv_tripdata_2023-01.parquet"
    job = cliente_bq.load_table_from_uri(uri, "nyc_taxi.viajes_fvh", job_config=job_config)
    job.result()
    print(f"Datos cargados: {cliente_bq.get_table('nyc_taxi.viajes_fvh').num_rows} filas")

@task
def transformar_datos():
    cliente_bq = bigquery.Client(project='project-13385eff-5d97-4173-81d')

    sql_transformacion = """
    CREATE OR REPLACE TABLE nyc_taxi.viajes_fvh_limpio AS
    SELECT *,
        TIMESTAMP_DIFF(dropOff_datetime, pickup_datetime, MINUTE) AS duracion_min,
        EXTRACT(HOUR FROM pickup_datetime) as hora,
        FORMAT_TIMESTAMP('%A', pickup_datetime) as dia_semana,
        CASE 
            WHEN TIMESTAMP_DIFF(dropOff_datetime, pickup_datetime, MINUTE) < 10 THEN 'corto'
            WHEN TIMESTAMP_DIFF(dropOff_datetime, pickup_datetime, MINUTE) BETWEEN 10 AND 30 THEN 'medio'
            ELSE 'largo'
        END AS categoria_viaje
    FROM nyc_taxi.viajes_fvh
    WHERE TIMESTAMP_DIFF(dropOff_datetime, pickup_datetime, MINUTE) >= 1
    AND TIMESTAMP_DIFF(dropOff_datetime, pickup_datetime, MINUTE) <= 300
    """

    job = cliente_bq.query(sql_transformacion)
    job.result()

    tabla = cliente_bq.get_table('nyc_taxi.viajes_fvh_limpio')
    print(f"Tabla transformada: {tabla.num_rows} filas")


@flow
def pipeline_nyc_taxi():
    subir_a_gcs()
    cargar_a_bigquery()
    transformar_datos()

if __name__ == "__main__":
    pipeline_nyc_taxi()