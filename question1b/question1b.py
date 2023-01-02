import os
from obj import Cache
import requests
from google.cloud import bigquery
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import time

load_dotenv(find_dotenv())


def get_cached_departement(cache: Cache, meeting_point_id: int, lon: float, lat: float):
    departement_code = cache.departement_cached(meeting_point_id)
    if departement_code:
        return departement_code
    else:
        api_url = "https://api-adresse.data.gouv.fr/reverse"
        params = {'lon': lon, 'lat': lat}
        response = requests.get(api_url, params=params).json()
        departement_code_found = response['features'][0]['properties']['postcode'][:2] if \
        response['features'][0]['properties']['score'] > 0.7 else None
        cache.save_to_cache(meeting_point_id, departement_code_found)
        return departement_code_found


def generate_agg_dept(partnership_type: list = [], begin_date: str = '', end_date: str = ''):
    # try :

    start_time = time.time()
    client = bigquery.Client()
    query = f"""
        SELECT 
            count(distinct ls.Lesson_id) as count_lessons_booked,
            m.meeting_point_id,
            m.mp_longitude,
            m.mp_latitude
        FROM ( SELECT Lesson_id, Instructor_id, Meeting_point_id
                FROM `test_dataset.lessons` 
                WHERE (lesson_deleted_at is null or DATE(lesson_deleted_at) > CURRENT_DATE() )
                and DATE(Lesson_start_at) BETWEEN PARSE_DATE('%Y-%m-%d', @begin_date) and PARSE_DATE('%Y-%m-%d', @end_date )
            ) ls 
        INNER JOIN  (SELECT Lesson_id
                    FROM `test_dataset.bookings` 
                    WHERE (Booking_deleted_at is null or DATE(Booking_deleted_at) > CURRENT_DATE())
            ) b ON b.Lesson_id = ls.Lesson_id
        INNER JOIN (SELECT instructor_id
                    FROM `test_dataset.instructors` 
                    WHERE (partnership_type in UNNEST(@partnership_type) )
            ) i ON ls.Instructor_id = i.instructor_id
        INNER JOIN `test_dataset.meeting_points` m ON ls.Meeting_point_id = m.meeting_point_id
        GROUP BY m.meeting_point_id,
            m.mp_longitude,
            m.mp_latitude
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("partnership_type", "STRING", partnership_type),
            bigquery.ScalarQueryParameter("begin_date", "STRING", begin_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    df = query_job.to_dataframe()

    cache = Cache('cache_departement.db')
    df["dept_code"] = df.apply(
        lambda row: get_cached_departement(cache, row["meeting_point_id"], row["mp_longitude"], row["mp_latitude"]),
        axis=1)

    df_groupby = df.groupby(["dept_code"])["count_lessons_booked"].sum()
    print("--- %s seconds ---" % (time.time() - start_time))
    print(df_groupby)
    # except :
    #  return 'Error'

    ### to do ###
    # if partnership not exist
    # if partnershipt not selected
    # if end_date < begin_date
    # if end date not a date
    # if begin_date not a date
    # if lots and lots of meeting point
    # pytest with mock bigquery
    # readme
    # doc string
    #


if __name__ == "__main__":
    # ---- to del----
    pd.options.display.width = None
    pd.options.display.max_columns = None
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 3000)
    # ---------------
    generate_agg_dept(['SASU', 'ME', 'SARL', 'SAS', 'EI'], "2019-01-01", "2022-02-01")
    generate_agg_dept(['ME', 'EI'], "2020-01-01", "2020-02-01")
    generate_agg_dept(['ME', 'EI'], "2020-01-01", "2020-02-01")
