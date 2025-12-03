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
            level TEXT,
            message TEXT,
            status TEXT
        )""")

        # 3. 用户表
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            created_at DATETIME
        )""")
        
        # 插入默认管理员
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users VALUES ('admin', '123456', 'admin', ?)", 
                           (datetime.datetime.now(),))
        
        conn.commit()
        conn.close()

    # --- 数据记录相关 ---
    def insert_record(self, data: dict):
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO monitor_logs (timestamp, depth, velocity, flow_rate, fr_number, flow_state, float_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
             data['depth'], data['velocity'], data['flow_rate'], data['fr'], data['state'], data['float_count'])
        )
        conn.commit()
        conn.close()

    def get_history(self, limit=100):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM monitor_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def export_to_csv(self, filename="export_data.csv"):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM monitor_logs")
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(cursor)
        conn.close()
        return os.path.abspath(filename)

    # --- 用户认证与注册相关 ---
    def authenticate(self, username, password):
        conn = self.get_connection()
        cursor = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def user_exists(self, username):
        conn = self.get_connection()
        cursor = conn.execute("SELECT 1 FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def register_user(self, username, password):
        """注册新用户，返回 (Success, Message)"""
        if self.user_exists(username):
            return False, "用户名已存在"
        
        try:
            conn = self.get_connection()
            conn.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                         (username, password, 'user', datetime.datetime.now()))
            conn.commit()
            conn.close()
            return True, "注册成功"
        except Exception as e:
            return False, f"数据库错误: {str(e)}"