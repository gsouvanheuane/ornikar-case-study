import os
from src.question1b.obj import Cache
import requests
from google.cloud import bigquery
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import time
import datetime

load_dotenv(find_dotenv())


def validate(date_text: str) -> None:
    """
    Function validate.
    Use this fonction to check if the input is a date in the format YYYY-MM-DD
    :param date_text (str): the string to validate
    """
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, it should be YYYY-MM-DD")


def get_cached_departement(cache: Cache, meeting_point_id: int, lon: float, lat: float) -> int:
    """
    Function get_cached_departement.
    Use this function to get the departement where belong the meeting_point_id. If the meeting_point departement is
    not cached yet, the result will be saved for later use. To determine the departement of a meeting_point_id,
    this function will call the Reverse Geocoding API created by the France gouvernment
    (see https://adresse.data.gouv.fr/api-doc/adresse#reverse)
    :param cache(Cache):  instance of the object Cache
    :param meeting_point_id(int): id of the meeting point to fetch the cached departement code associated
    :param lon (float): longitude of the meeting point
    :param lat(float): latitude of the meeting point
    :return: the department code(int)
    """
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


def generate_agg_dept(partnership_type: list = [], begin_date: str = '', end_date: str = '') -> dict:
    """
    Function generate_agg_dept.
    :param partnership_type(list): list of the partnership_type
    :param begin_date(str): begin date of the aggregation, the format should be YYYY-MM-DD
    :param end_date(str): end date of the aggregation, the format should be YYYY-MM-DD
    :return: dictionary of each departement with the number of lesson booked according to the param selected
    """
    try:
        try:
            validate(begin_date)
            validate(end_date)
        except ValueError:
            raise ValueError('⚠️Incorrect data format, it should be YYYY-MM-DD. Try again')
        else :
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

            if not df.empty:
                cache = Cache(os.path.join("src","question1b",'cache_departement.db'))
                df["dept_code"] = df.apply(
                    lambda row: get_cached_departement(cache, row["meeting_point_id"], row["mp_longitude"],
                                                       row["mp_latitude"]),
                    axis=1)

                df_groupby = df.groupby(["dept_code"])["count_lessons_booked"].sum()
                print("--- The query took %s seconds ---" % (time.time() - start_time))
                return df_groupby.to_dict()
            else:
                return {}
    except Exception:
        raise


def prompt():
    """
    Function prompt.
    Use this function to launch the prompt to use generate_agg_dept()
    """
    print("Welcome")
    print("Please type Ctrl+Z if you want to quit the script")
    while True:
        try:
            partnership_input = input('Enter partnerships, you can pass multiple partnership separated by space: ')
            partnership_input_list = partnership_input.upper().split()
            begin_date_input = input('Enter a begin date following the date format YYYY-MM-DD: ')
            try:
                validate(begin_date_input)
            except ValueError:
                raise ValueError('⚠️Incorrect data format, it should be YYYY-MM-DD. Try again')

            end_date_input = input('Enter a end date following the date format YYYY-MM-DD: ')
            try:
                validate(end_date_input)
            except ValueError:
                raise ValueError('⚠️Incorrect data format, it should be YYYY-MM-DD. Try again')
            else:
                print(
                    f'Generating the number of lessons booked by sub-region for partnerships {partnership_input_list} from {begin_date_input} to {end_date_input}')
                list_result = generate_agg_dept(partnership_input_list, begin_date_input, end_date_input)
                if len(list_result) == 0:
                    print('No result found. Try to modify the parameters')
                else:
                    print(list_result)
                replay = input('Run again? (y/n) ')
                if replay.lower() == 'n':
                    break

        except ValueError as e:
            print(e)
        except Exception as e:
            print('Something went wrong: ', e)
            break

