import sqlite3

conn = sqlite3.connect("./Auth.db")
curr = conn.cursor()

# curr.execute("""SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;""")

# curr.execute("""SELECT IP, CASE 
#                                 WHEN Method IN ('GET' , 'HEAD') 
#                                 THEN 'Download' 
#                                 ELSE 'Upload'
#                                 END AS "Action Type", 
#                 Bandwidth
#                 FROM Requests
#                 WHERE dbTimestamp >= ? AND dbTimestamp <= ?
#                 ORDER BY Bandwidth DESC""",("2026-06-01T02:17", "2026-06-22T02:17"))

curr.execute("""SELECT * FROM Requests""")

for row in curr.fetchall():
    print(row)

conn.close()