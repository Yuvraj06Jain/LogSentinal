import os
import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

#Database Folder:
dbFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), "Databases"))

async def writing_data(fileType: str, events: list, requests: list, fileCounter: tuple):
    db_path = os.path.join(dbFolder, f"{fileType}.db")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        # Events Table for non aggregate data

        create_table = """CREATE TABLE IF NOT EXISTS Events (
                        dbTimestamp TEXT,
                        category TEXT,
                        detail TEXT)"""

        cur.execute(create_table)
        cur.execute("CREATE INDEX IF NOT EXISTS ids_events_ts ON Events (dbTimestamp)")
        
        cur.executemany("""INSERT INTO Events (dbTimestamp, category, detail) VALUES (?, ?, ?)""",
                        [(e['Timestamp'], e['category'], e['detail']) for e in events])


        # Requests table for aggregate data
        if requests:
            python_to_sql = {str: "TEXT", int: "INTEGER", float: "REAL"}  
            columns = ", ".join(f"{col} {python_to_sql.get(type(val), 'TEXT')}" for col, val in requests[0].items())
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
    db_path = os.path.join(dbFolder, f"{fileType}.db")

    if not os.path.exists(db_path):
        return {"Status" : "Success", "Message" : "Historical Data Doesn't exists", "Data" : {}}
    
    try:
        data = {}

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        curr = conn.cursor()
        
        curr.execute("""SELECT category, detail
                        FROM Events
                        WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                        ORDER BY dbTimestamp DESC""",(from_ts, to_ts))
        rows = curr.fetchall()

        for category, detail in rows:
            if category not in data:
                data[category] = []
            data[category].append(json.loads(detail))
        
        if fileType != "Auth":                           # Auth has a different structure of Requests as compared to Nginx and Apache

            try:                                                                            # URL's Accessed Counter
                curr.execute("""SELECT URL, Method, COUNT(*) as Count
                            FROM Requests
                            WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                            GROUP BY URL, Method
                            ORDER BY Count DESC
                            """,(from_ts, to_ts))
                data['URLs Accessed Counter'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['URLs Accessed Counter'] = []

            try:                                                                            # Suspicious IPs with No. of 404 Errors >= 40%
                curr.execute("""SELECT IP, Type, COUNT(*) AS "Total Reqs", 
                            COUNT(CASE WHEN Status_code = "404" THEN 1 END) AS "404 Reqs",
                            COUNT(CASE WHEN Status_code = "404" THEN 1 END) * 1.0/COUNT(*) AS Ratio
                            FROM Requests
                            WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                            GROUP BY IP
                            HAVING Ratio >= 0.4
                            ORDER BY Ratio DESC, "404 Reqs" DESC""", (from_ts, to_ts))
                data['Suspicious IPs with No. of 404 errors >= 40%'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['Suspicious IPs with No. of 404 errors >= 40%'] = []


            try:                                                                              # Bandwidth Analysis
                curr.execute("""SELECT IP, Type, CASE WHEN Method IN ('GET' , 'HEAD') THEN 'Download' ELSE 'Upload' END AS "Action Type", Bandwidth
                            FROM Requests
                            WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                            ORDER BY CAST(Bandwidth AS INTEGER) DESC""",(from_ts, to_ts))
                data['Bandwidth Analysis'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['Bandwidth Analysis'] = []

            try:                                                                              # No. of requests from different Countries
                curr.execute("""SELECT Country, COUNT(*) AS Count
                                FROM Requests
                                WHERE Country != "-" AND Country != "Non-Public IP" AND dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY Country
                                ORDER BY Count DESC""", (from_ts, to_ts))
                data['No. of requests from different Countries'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['No. of requests from different Countries'] = []

            try:                                                                              # No. of times a blocked IP makes a request
                curr.execute("""SELECT IP, Type, COUNT(*) AS Count
                                FROM Requests
                                WHERE Blocked = 1 AND dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY IP
                                ORDER BY Count DESC""",(from_ts, to_ts))
                data['No. of times a blocked IP makes a requests'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['No. of times a blocked IP makes a requests'] = []
                        
        else:
            
            try:                                                                                # No. of Failed login attempts per IP
                curr.execute("""SELECT IP, Type, COUNT(*) AS Count
                                FROM Requests
                                WHERE Status_code = 'Failed' AND dbTimestamp >= ? AND dbTimestamp <= ?
                                ORDER BY Count DESC""",(from_ts, to_ts))
                data['No. of Failed login attempts per IP'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['No. of Failed login attempts per IP'] = []

            try:                                                                                # No. of requests from different Countries
                curr.execute("""SELECT Country, COUNT(*) AS Count
                                FROM Requests
                                WHERE Country != "-" AND Country != "Non-Public IP" AND dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY Country
                                ORDER BY Count DESC""", (from_ts, to_ts))
                data['No. of requests from different Countries'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['No. of requests from different Countries'] = []

            try:                                                                                 # No. of times a blocked IP makes a requests
                curr.execute("""SELECT IP, Type, COUNT(*) AS Count
                                FROM Requests
                                WHERE Blocked = 1 AND dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY IP
                                ORDER BY Count DESC""",(from_ts, to_ts))
                data['No. of times a blocked IP makes a requests'] = [dict(row) for row in curr.fetchall()]
            except sqlite3.OperationalError:
                data['No. of times a blocked IP makes a requests'] = []

        conn.commit()
        conn.close()
        
        return {"Status" : "Success", "Message" : f"Fetching historical data for {fileType} logs successful...", "Data" : data}
    
    except:
        return {"Status" : "Failed", "Message" : "Error Recieved. Please Try Again...", "Data" : {}}
    


def summary(from_ts: str, to_ts: str, selected: dict):
    aggregateData = ['URLs Accessed Counter', 'Suspicious IPs with No. of 404 errors >= 40%', 'No. of Failed login attempts per IP', 'Bandwidth Analysis', 'No. of requests from different Countries', 'No. of times a blocked IP makes a requests']
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown_str = f"""### Summary dated on {now} [From: {from_ts}, To: {to_ts}]\n\n---\n\n"""
    for file in selected.keys():
        if not selected[file]:
            continue

        string = f"""### {file}\n\n---\n\n"""

        db_path = os.path.join(dbFolder, f"{file}.db")

        if not os.path.exists(db_path):
            string += """There exists no Database for the given log type.\n\n---\n\n---\n\n"""
            markdown_str += string 
            continue

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()

        for field in selected[file]:

            if field not in aggregateData:
                sql_query = """SELECT detail
                            FROM Events
                            WHERE dbTimestamp >= ? AND dbTimestamp <= ? AND category = ?
                            ORDER BY dbTimestamp 
                            LIMIT 10
                            """
                
                try:
                    curr.execute(sql_query, (from_ts, to_ts, field))
                    
                    field_data = [json.loads(data_str['detail']) for data_str in curr.fetchall()]
                    df_md = pd.DataFrame(field_data).to_markdown()

                    string += f"""**{field}**\n\n""" + df_md + """\n\n---\n\n"""

                except Exception as e:
                    string += f"""**{field}**\n\n""" + "\nFailed to load the data.\n" + """\n\n---\n\n"""

            else:

                if (field == "URLs Accessed Counter"):
                    sql_query = """SELECT URL, Method, COUNT(*) as Count
                                FROM Requests
                                WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY URL, Method
                                ORDER BY Count DESC
                                LIMIT 10"""
                    
                elif (field == "Suspicious IPs with No. of 404 errors >= 40%"):
                    sql_query = """SELECT IP, Type, COUNT(*) AS "Total Reqs", 
                                COUNT(CASE WHEN Status_code = "404" THEN 1 END) AS "404 Reqs",
                                COUNT(CASE WHEN Status_code = "404" THEN 1 END) * 1.0/COUNT(*) AS Ratio
                                FROM Requests
                                WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY IP
                                HAVING Ratio >= 0.4
                                ORDER BY Ratio DESC, "404 Reqs" DESC
                                LIMIT 10"""
                
                elif (field == "Bandwidth Analysis"):
                    sql_query = """SELECT IP, Type, CASE WHEN Method IN ('GET' , 'HEAD') THEN 'Download' ELSE 'Upload'END AS "Action Type", Bandwidth
                                FROM Requests
                                WHERE dbTimestamp >= ? AND dbTimestamp <= ?
                                ORDER BY CAST(BANDWIDTH AS INTEGER) DESC
                                LIMIT 10"""
                
                elif (field == "No. of Failed login attempts per IP"):
                    sql_query = """SELECT IP, Type, COUNT(*) AS Count
                                FROM Requests
                                WHERE Status_code = 'Failed' AND dbTimestamp >= ? AND dbTimestamp <= ?
                                ORDER BY Count DESC
                                LIMIT 10"""
                    
                elif (field == "No. of requests from different Countries"):
                    sql_query = """SELECT Country, COUNT(*) AS Count
                                FROM Requests
                                WHERE Country != "-" AND Country != "Non-Public IP" AND Country != "Database Not Ready" AND dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY Country
                                ORDER BY Count DESC
                                LIMIT 10"""
                
                elif (field == 'No. of times a blocked IP makes a requests'):
                    sql_query = """SELECT IP, Type, COUNT(*) as Count
                                FROM Requests
                                WHERE Blocked = 1 dbTimestamp >= ? AND dbTimestamp <= ?
                                GROUP BY IP
                                ORDER BY Count DESC
                                LIMIT 10"""
                    
                try:
                    curr.execute(sql_query, (from_ts, to_ts))
                    field_data = [dict(row) for row in curr.fetchall()]

                    if field_data == []:
                        string = f"""**{field}**\n\n""" + "\nNo Data Present\n" + """\n\n---\n\n""" 
                        continue

                    df_md = pd.DataFrame(field_data).to_markdown()

                    string += f"""**{field}**\n\n""" + df_md + """\n\n---\n\n"""

                except sqlite3.Error as e:
                    string += f"""**{field}**\n\n""" + "\nFailed to load the data.\n" + """\n\n---\n\n"""

        conn.commit()
        markdown_str += string + """\n\n---\n\n---\n\n"""
        conn.close()

    return markdown_str

def deleteData():

    now = datetime.now()
    thirtydayspast = (now - timedelta(days=30)).isoformat()

    for fileType in ["Apache", "Nginx", "Auth"]:
        db_path = os.path.join(dbFolder, f"{fileType}.db")
        if not os.path.exists(db_path):
            continue

        conn = sqlite3.connect(db_path)
        curr = conn.cursor()

        try:

            query = """SELECT name FROM sqlite_master
                    WHERE type='table'
                    ORDER BY name;"""
            curr.execute(query)
            tables = [row[0] for row in curr.fetchall()]
            for table in tables:

                if table == 'fileCounter':
                    continue

                query = f"""DELETE FROM {table}
                        WHERE dbTimestamp < ?"""
                curr.execute(query, (thirtydayspast,))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[LogSentinal] Deletion of Data older than a month Failed for {fileType}.db, Error : {e}")
        finally:
            conn.close()