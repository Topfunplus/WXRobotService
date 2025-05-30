#!/usr/bin/python

import sqlite3

class SQLiteHelper:
    def __init__(self, db_name):
        """
        初始化SQLiteHelper对象。

        Args:
            db_name (str): 数据库文件名。
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        连接到SQLite数据库。
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"成功连接到数据库: {self.db_name}")
        except sqlite3.Error as e:
            print(f"连接数据库失败: {e}")
            self.conn = None
            self.cursor = None
        return self.conn

    def close(self):
        """
        关闭数据库连接。
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print(f"成功关闭数据库连接: {self.db_name}")

    def create_table(self, table_name, columns):
        """
        创建表。

        Args:
            table_name (str): 表名。
            columns (str): 表的列定义，例如 "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER"。
        """
        try:
            if not self.conn:
                print("请先连接数据库。")
                return
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(sql)
            self.conn.commit()
            print(f"表 '{table_name}' 创建成功或已存在。")
        except sqlite3.Error as e:
            print(f"创建表 '{table_name}' 失败: {e}")

    def insert_data(self, table_name, data):
        """
        插入数据。

        Args:
            table_name (str): 表名。
            data (dict): 要插入的数据，字典的键为列名，值为对应的值。
        """
        try:
            if not self.conn:
                print("请先连接数据库。")
                return
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = tuple(data.values())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, values)
            self.conn.commit()
            print("数据插入成功。")
        except sqlite3.Error as e:
            print(f"数据插入失败: {e}")

    def select_data(self, table_name, columns='*', condition=None, order_by=None):
        """
        查询数据。

        Args:
            table_name (str): 表名。
            columns (str, optional): 要查询的列名，默认为 '*' (所有列)。
            condition (str, optional): 查询条件，例如 "age > 20"。默认为 None (无条件)。
            order_by (str, optional): 排序字段，例如 "timestamp"。默认为 None (不排序)。

        Returns:
            list: 查询结果，每一行是一个元组。
        """
        try:
            if not self.conn:
                print("请先连接数据库。")
                return None
            sql = f"SELECT {columns} FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"
            if order_by:
                sql += f" ORDER BY {order_by}"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"查询数据失败: {e}")
            return None
    def update_data(self, table_name, data, condition):
        """
        更新数据。

        Args:
            table_name (str): 表名。
            data (dict): 要更新的数据，字典的键为列名，值为对应的新值。
            condition (str): 更新条件，例如 "id = 1"。
        """
        try:
            if not self.conn:
                print("请先连接数据库。")
                return
            set_clause = ', '.join([f"{key} = ?" for key in data])
            values = tuple(data.values())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            self.cursor.execute(sql, values)
            self.conn.commit()
            print("数据更新成功。")
        except sqlite3.Error as e:
            print(f"数据更新失败: {e}")

    def delete_data(self, table_name, condition):
        """
        删除数据。

        Args:
            table_name (str): 表名。
            condition (str): 删除条件，例如 "id = 1"。
        """
        try:
            if not self.conn:
                print("请先连接数据库。")
                return
            sql = f"DELETE FROM {table_name} WHERE {condition}"
            self.cursor.execute(sql)
            self.conn.commit()
            print("数据删除成功。")
        except sqlite3.Error as e:
            print(f"数据删除失败: {e}")

# 示例用法
# if __name__ == "__main__":
#     db_helper = SQLiteHelper('wechat.db')
#     conn = db_helper.connect()

#     if conn:
#         # 创建表
#         db_helper.create_table('users', 'id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER')

#         # 插入数据
#         db_helper.insert_data('users', {'name': 'Alice', 'age': 30})
#         db_helper.insert_data('users', {'name': 'Bob', 'age': 25})

#         # 查询数据
#         print("所有用户:")
#         all_users = db_helper.select_data('users')
#         for user in all_users:
#             print(user)

#         print("\n年龄大于28岁的用户:")
#         older_users = db_helper.select_data('users', condition='age > 28')
#         for user in older_users:
#             print(user)

#         # 更新数据
#         db_helper.update_data('users', {'age': 31}, 'name = "Alice"')

#         # 查询更新后的数据
#         print("\n更新后的Alice信息:")
#         alice = db_helper.select_data('users', condition='name = "Alice"')
#         for user in alice:
#             print(user)

#         # 删除数据
#         db_helper.delete_data('users', 'name = "Bob"')

#         # 查询删除后的数据
#         print("\n删除Bob后的用户:")
#         remaining_users = db_helper.select_data('users')
#         for user in remaining_users:
#             print(user)

#         # 关闭连接
#         db_helper.close()