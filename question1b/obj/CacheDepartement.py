import sqlite3

class Cache(object):
    def __init__(self, fn='cache.db'):
       self.conn = conn = sqlite3.connect(fn)
       cur = conn.cursor()
       cur.execute("""CREATE TABLE IF NOT EXISTS meeting_point_departement (
                   meeting_point_id INT PRIMARY KEY,
                   departement_code INT 
                   )
        """)
       conn.commit()

    def departement_cached(self, meeting_point_id):
        cur = self.conn.cursor()
        cur.execute('SELECT departement_code FROM meeting_point_departement WHERE meeting_point_id=?', (meeting_point_id,))
        res = cur.fetchone()
        if res is None: return False
        return res[0]

    def save_to_cache(self, meeting_point_id, departement_code):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO meeting_point_departement(meeting_point_id, departement_code) VALUES(?, ?)',
                    (meeting_point_id, departement_code ))
        self.conn.commit()
