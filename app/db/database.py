# app/db/database.py
import sqlite3
import datetime
import csv
import os

class DatabaseManager:
    def __init__(self, db_name="canal_data.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def create_tables(self):
        conn = self.get_connection()
        # 1. 监控日志表
        conn.execute("""
        CREATE TABLE IF NOT EXISTS monitor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            depth REAL, velocity REAL, flow_rate REAL, fr_number REAL, 
            flow_state TEXT, float_count INTEGER
        )""")
        
        # 2. 预警记录表
        conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            level TEXT,    -- RED, YELLOW
            message TEXT,
            status TEXT    -- UNREAD, RESOLVED
        )""")

        # 3. 用户表
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )""")
        
        # 插入默认管理员 (生产环境请务必使用哈希加密密码)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users VALUES ('admin', '123456', 'admin')")
        
        conn.commit()
        conn.close()

    def insert_record(self, data: dict):
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO monitor_logs (timestamp, depth, velocity, flow_rate, fr_number, flow_state, float_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
             data['depth'], data['velocity'], data['flow_rate'], data['fr'], data['state'], data['float_count'])
        )
        conn.commit()
        conn.close()

    def add_alert(self, level, message):
        conn = self.get_connection()
        conn.execute("INSERT INTO alerts (timestamp, level, message, status) VALUES (?, ?, ?, ?)",
                     (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message, "UNREAD"))
        conn.commit()
        conn.close()

    def get_history(self, limit=100):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM monitor_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def authenticate(self, username, password):
        conn = self.get_connection()
        cursor = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def export_to_csv(self, filename="export_data.csv"):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM monitor_logs")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cursor.description]) # 写入表头
            writer.writerows(cursor)
        conn.close()
        return os.path.abspath(filename)