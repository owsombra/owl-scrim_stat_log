'''
from sqlalchemy import exc 
from sqlalchemy import create_engine 
from mysql_auth import mysql_auth
import pandas as pd
import pymysql

def get_update_tablelist():
    teamname = 'NYE'
    rawdb_dbname = teamname + '_Rawdb'
    db_login = mysql_auth.auth_info
    db_conn = pymysql.connect(host = db_login['hostname'], port = int(db_login['port']), user = db_login['username'], passwd = db_login['pwd'], db = rawdb_dbname)
    cursor = db_conn.cursor()
    sql = """
        select tablename from toFinalstatTable where isReflected = false;;
    """
    cursor.execute(sql)
    result = cursor.fetchall()
    update_list = []
    for row_data in result:
        update_list.append(row_data[0])

    return update_list

    #rawdb_engine = create_engine('mysql+pymysql://' + db_login['username'] + ':' + db_login['pwd'] + '@' + db_login['hostname'] + ':' + str(db_login['port']) + '/' + rawdb_dbname , echo=False)
    #connection = rawdb_engine.connect()
    #result = rawdb_engine.execute("SHOW Tables;")
    #print(result.fetchall())

def read_tables_as_df(update_list):
    db_update_list = update_list
    table_df_list = []
    teamname = 'NYE'
    rawdb_dbname = teamname + '_Rawdb'
    db_login = mysql_auth.auth_info
    db_conn = pymysql.connect(host = db_login['hostname'], port = int(db_login['port']), user = db_login['username'], passwd = db_login['pwd'], db = rawdb_dbname)
    cursor = db_conn.cursor()

    for table_name in update_list:
        table_df = pd.read_sql(
        sql=f"SELECT * FROM `{table_name}`",
        con=db_conn,
        )
        table_df_list.append(table_df)

    return table_df_list
    
def export_to_csv(df_input, tablename, save_dir='C:/Users/Sqix_OW/Desktop/'):
    df_input.to_csv(save_dir + str(i) + '.csv')
#input_df.to_csv('C:/Users/Sqix_OW/Desktop/test.csv')
    
update_list = get_update_tablelist()
print(update_list)
#read_tables_as_df(update_list)
rawdb_data = read_tables_as_df(update_list)
#print(rawdb_data[0])
for i in range(0, len(update_list)):
    export_to_csv(rawdb_data[i], update_list[i])

'''
import pandas as pd 
import numpy as np 
import glob
from tqdm import tqdm
from ScrimLog import *
from PeriEventTimeHistogram import *

teamname = 'NYE'
scrim_sql = ScrimLog().update_FinalStat_to_sql(teamname)
