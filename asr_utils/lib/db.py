import pymysql

class DB():
    def __init__(self, server_name, username, password, db_name, port=3306):
        self.server_name = server_name
        self.username = username
        self.password = password
        self.db_name = db_name
        self.port = port

        self.conn = None

    def build_connect(self):
        self.conn = pymysql.connect(host = self.server_name, user = self.username, password = self.password, database =  self.db_name, port=self.port)

    def close_connect(self):
        self.conn.close()

    def select(self, table, retrieve_str="*", condition_str="1"):
        with self.conn.cursor() as cursor:
            sql = "SELECT %s FROM %s WHERE %s" % (retrieve_str, table, condition_str)

            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                return results
            except:
                print("Failed to select (sql: {})".format(sql))

    def insert(self, table, set_str, value_str):
        with self.conn.cursor() as cursor:
            sql = "INSERT INTO %s %s VALUES %s" % (table, set_str, value_str)

            try:
                cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("Failed to insert (sql: {})".format(sql))

    def update(self, table, set_str, condition_str):
        with self.conn.cursor() as cursor:
            sql = "UPDATE %s SET %s WHERE %s" % (table, set_str, condition_str)

            try:
                cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("Failed to update (sql: {})".format(sql))

    def delete(self, table, condition_str):
        with self.conn.cursor() as cursor:
            sql = "DELETE FROM %s WHERE %s" % (table, condition_str)

            try:
                cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("Failed to delete (sql: {})".format(sql))
