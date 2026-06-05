from src.models.db.handler_fb_db import ConnectionDBFireBird

with ConnectionDBFireBird() as con:
    cur = con.cursor()

    cur.execute("SELECT * FROM RICADPAC WHERE id <= 5")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()