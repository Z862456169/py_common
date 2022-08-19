import cx_Oracle


class ConnectOracle:
    def __init__(self):
        self.db_user = 'MESSTANDARDDEV'
        self.password = '123456'
        self.db_data = '192.168.1.221:1521/tzinfo'

    def connect_oracle(self, sql):
        try:
            # 连接数据库
            db = cx_Oracle.connect(self.db_user, self.password, self.db_data)
            print("Oracle数据库版本：", db.version)
            # 创建游标
            curs = db.cursor()
            # sql = 'SELECT * FROM MESAKCOMEDEV.MC_WAFER_DEFECT'
            # sql = 'SELECT * FROM {table_user_name}.{table_name}'.format(table_user_name='MESAKCOMEDEV',
            #                                                             table_name='MC_WAFER_DEFECT')
            results = curs.execute(sql)  # 执行sql
            rows = results.fetchall()  # 获取所有数据
            # print('total_count:', len(rows))
            # for index, row in enumerate(rows):
            #     print('%s:%s' % (index, row))
        except Exception as error:
            print("error:", error)
        finally:
            # 关闭游标和数据库
            curs.close()
            db.close()
        return rows


if __name__ == '__main__':
    # sql = "SELECT ENTIRE_DECIMAL_CODE FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE PARENT_ID IN (SELECT ID FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO WHERE WAFER_NO IN ('02204020111000011'))"
    sql = "SELECT ENTIRE_DECIMAL_CODE FROM MESAKCOMEDEV.MC_BASE_WAFER_INFO "
    con = ConnectOracle()
    result = con.connect_oracle(sql)
    print(result)
