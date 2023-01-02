import os
from google.cloud import bigquery
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()

start_time = time.time()
client = bigquery.Client()

query = """
WITH top5_instructor as (
    SELECT 
           array_agg(instructor_id order by count_lessons_booked desc limit 5) as arr_top5
    FROM (
        SELECT ls.instructor_id, 
            count(distinct ls.Lesson_id) as count_lessons_booked
        FROM ( SELECT instructor_id, Lesson_id
                FROM `test_dataset.lessons` 
                WHERE (lesson_deleted_at is null or CAST(lesson_deleted_at as DATE) > CURRENT_DATE() )
                and EXTRACT(QUARTER from Lesson_start_at) = 3
                and EXTRACT(YEAR from Lesson_start_at) =  2020
            ) ls
        INNER JOIN ( SELECT Lesson_id
                    FROM `test_dataset.bookings` 
                    WHERE (Booking_deleted_at is null or CAST(Booking_deleted_at as DATE) > CURRENT_DATE())
            ) b
          ON b.Lesson_id = ls.Lesson_id
        GROUP BY ls.instructor_id
        )
)
SELECT DISTINCT instructor_id, 
    NTH_VALUE(Lesson_start_at, 50) 
        OVER (PARTITION BY instructor_id ORDER BY Lesson_start_at ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as lessons_50th
FROM ( SELECT instructor_id, Lesson_start_at, Lesson_id
        FROM `test_dataset.lessons`
        WHERE (lesson_deleted_at is null or DATE(lesson_deleted_at) > CURRENT_DATE() )
        and instructor_id in ( select top5 from top5_instructor, UNNEST(arr_top5) top5)
    ) ls 
INNER JOIN (SELECT Lesson_id
            FROM `test_dataset.bookings`
            WHERE (Booking_deleted_at is null or DATE(Booking_deleted_at) > CURRENT_DATE())
    ) b 
ON b.Lesson_id = ls.Lesson_id
"""

query_job = client.query(query) # API request
rows = query_job.to_dataframe()  # Waits for query to finish


print("--- %s seconds ---" % (time.time() - start_time))

print(rows)