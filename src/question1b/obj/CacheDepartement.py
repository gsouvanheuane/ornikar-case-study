import sqlite3
import os
class Cache(object):
    """
    Class Cache
    This class will create a sqlite database if it does not exist, this database will contain the cached departement.
    It will help to read and write into the database.

    Attributes:
        - path(str): path where to find the sqlite database which will contains cached departement
    Functions:
        - departement_cached(self, meeting_point_id): Fetch the departement of a meeting_point if it is cached in the database
        - save_to_cache(self, meeting_point_id, departement_code): Insert new value to cache
    """
    def __init__(self, path: str ='cache.db'):
       self.conn = conn = sqlite3.connect(path)
       cur = conn.cursor()
       cur.execute("""CREATE TABLE IF NOT EXISTS meeting_point_departement (
                   meeting_point_id INT PRIMARY KEY,
                   departement_code INT 
                   )
        """)
       conn.commit()

    def departement_cached(self, meeting_point_id) -> int:
        """
        Function departement_cached.
        Use this function to fetch the departement of a meeting_point if it is cached in the database
        :param meeting_point_id: id of the meeting_point
        :return: the departement_code
        """
        cur = self.conn.cursor()
        cur.execute('SELECT departement_code FROM meeting_point_departement WHERE meeting_point_id=?', (meeting_point_id,))
        res = cur.fetchone()
        if res is None: return False
        return res[0]

    def save_to_cache(self, meeting_point_id: int, departement_code: int) -> None:
        """
        Function save_to_cache.
        Use this function to cache the departement_code associated to the meeting_point
        :param meeting_point_id(int): id of the meeting_point to cached
        :param departement_code(int): departement_code to cached
        """
        cur = self.conn.cursor()
        cur.execute('INSERT INTO meeting_point_departement(meeting_point_id, departement_code) VALUES(?, ?)',
                    (meeting_point_id, departement_code ))
        self.conn.commit()

