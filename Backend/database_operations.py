import os
import json
import sqlite3

async def writing_data(fileType: str, events: list, requests: list, fileCounter: tuple):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Databases", f"{fileType}.db")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        # Events Table for non aggregate data
        create_table = """CREATE TABLE IF NOT EXISTS Events (
                        Timestamp TEXT,
                        category TEXT,
                        detail TEXT)"""

        cur.execute(create_table)
        cur.execute("CREATE INDEX IF NOT EXISTS ids_events_ts ON Events (Timestamp)")
        
        cur.executemany("""INSERT INTO Events (Timestamp, category, detail) VALUES (?, ?, ?)""",
                        [(e['Timestamp'], e['category'], e['detail']) for e in events])


        # Requests table for aggregate data
        if requests:
            python_to_sql = {str: "TEXT", int: "INTEGER", float: "REAL"}  
            columns = ", ".join(f"{col} {python_to_sql.get(type(val), "TEXT")}" for col, val in requests[0].items())
            create_table = f"CREATE TABLE IF NOT EXISTS Requests ({columns})"
            cur.execute(create_table)
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_Requests_ts ON Requests (dbTimestamp)")

            cols = ", ".join(f"{col}" for col in requests[0].keys())
            placeholders = ", ".join("?"*len(requests[0]))
            vals = [tuple(x.values()) for x in requests]
            insert_sql = f"INSERT INTO Requests ({cols}) VALUES ({placeholders})"
            cur.executemany(insert_sql, vals)

        # Updating the lines successfully read.

        create_table = f"""CREATE TABLE IF NOT EXISTS fileCounter (
                        FileName TEXT PRIMARY KEY, 
                        LinesProcessed INTEGER)"""
        cur.execute(create_table)

        insert_sql = f"""INSERT INTO fileCounter (FileName, LinesProcessed) VALUES (?, ?)
                        ON CONFLICT(FileName) DO UPDATE SET LinesProcessed = excluded.LinesProcessed"""
        cur.execute(insert_sql, (fileCounter[0], fileCounter[1]))

        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()



async def getData(fileType, from_ts, to_ts):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Databases", f"{fileType}.db")

    if not os.path.exists(db_path):
        return {"Status" : "Success", "Message" : "Historical Data Doesn't exists"}
    
    try:
        data = {}

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        curr = conn.cursor()
        
        curr.execute("""SELECT category, detail
                        FROM Events
                        WHERE Timestamp >= ? AND Timestamp <= ?
                        ORDER BY Timestamp DESC""",(from_ts, to_ts))
        rows = curr.fetchall()

        for category, detail in rows:
            if category not in data:
                data[category] = []
            data[category].append(json.loads(detail))
        
        if fileType != "Auth":                           # Auth has a different structure of Requests as compared to Nginx and Apache

            curr.execute("""SELECT URL, Method, COUNT(*) as Count
                        FROM Requests
                        WHERE Timestamp >= ? AND Timestamp <= ?
                        GROUP BY URL, Method
                        ORDER BY Count DESC
                        """,(from_ts, to_ts))
            data['URLs Accessed Counter'] = [dict(row) for row in curr.fetchall()]

            curr.execute("""SELECT IP, COUNT(*) AS "Total Reqs", 
                        COUNT(CASE WHEN Status_code = "404" THEN 1 END) AS "404 Reqs",
                        COUNT(CASE WHEN Status_code = "404" THEN 1 END) * 1.0/COUNT(*) AS Ratio
                        FROM Requests
                        WHERE Timestamp >= ? AND Timestamp <= ?
                        GROUP BY IP
                        HAVING Ratio >= 0.4
                        ORDER BY Ratio DESC, "404 Reqs" DESC""", (from_ts, to_ts))
            data['Suspicious IPs with No. of 404 errors >= 40%'] = [dict(row) for row in curr.fetchall()]


            curr.execute("""SELECT IP, (CASE WHEN Method IN ('GET' , 'HEAD') THEN 'Download' ELSE 'Upload') AS "Action Type", Bandwidth
                        FROM Requests
                        WHERE Timestamp >= ? AND Timestamp <= ?
                        ORDER BY Bandwidth DESC""",(from_ts, to_ts))
            data['Bandwidth Analysis'] = [dict(row) for row in curr.fetchall()]

        else:

            curr.execute("""SELECT IP, COUNT(*) AS Count
                            FROM Requests
                            WHERE Status = 'Failed' AND Timestamp >= ? AND Timestamp <= ?
                            ORDER BY Count DESC""",(from_ts, to_ts))
            data['No. of Failed login attempts per IP'] = [dict(row) for row in curr.fetchall()]

        conn.close()
        
        return {"Status" : "Success", "Message" : data}
    
    except:
        return {"Status" : "Failed", "Message" : "Error Recieved. Please Try Again..."}