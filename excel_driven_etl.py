################################################################################
#
#   Date Written: 08/13/2025    By: Joseph P. Merten
#   This script will bring data from copy SQL tables and ETL them into a
#   new database/schema as outlined in etl_driver.xlsx.  The [config] tab in the 
#   workbook will identify the source and destination settings.  Connection details 
#   are stored in secrets.json.  
#   Each remaining tab will list the columns to be ETL'd into the specified 
#   destination schema/table.
#   
#   Future enhancements:
#   - Add meaningful print statemnts to track progress and validate values.
#   - Use the New_name column in the spreadsheets to rename 
#       columns in the destination table.
#   - Use the filter column in the spreadsheet to ETL a subset
#        of the source table.
#   - Use the dest_prefix and dest_suffix values in the [config] tab to add
#        a suffix/prefix to the table name.
#
################################################################################
#   Imports...
import os
import sys
import logging
import requests
from datetime import datetime
import json
# import snowflake.connector
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import shutil

################################################################################
#   Variables
secrets_location = r"./secrets.json"
excel_driver_location = r"./etl_driver.xlsx"
my_name = str(sys.argv[0])
log_file = str(sys.argv[0]).replace('.py', '.log')
sql_validate_columns = """
    select column_name 
    FROM information_schema.columns 
    WHERE table_name = '<<TABLE_NAME>>'
    ;"""
sql_query_source = """
    SELECT
        <<COLUMN_NAMES>>
    FROM <<TABLE_NAME>>
    ;"""


################################################################################
#   set up logging
try:
    print(f'Removing log file: {log_file}...')
    os.remove(log_file)
except:
    print(f'Log file: {log_file} not found...')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s \t%(levelname)s \t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=log_file
    )

################################################################################
#   functions...
def clear_screen():
    """
    Universal clear screen function regardless of environment.

    :param: none
    :returns: nothing
    :raises : nothing
    """
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

def get_conn_variables(my_db_key):
    """
    This function reads the secrets file and returns the connection variables for Which_db
    """
    # Open and read the JSON file
    with open(secrets_location, 'r') as file:
        data = json.load(file)
    # print("key on: ", my_db_key)
    # print(data['database_connections'][my_db_key])
    my_host = data['database_connections'][my_db_key]['host']
    my_db = data['database_connections'][my_db_key]['database']
    my_pw = data['database_connections'][my_db_key]['password']
    my_user = data['database_connections'][my_db_key]['username']
    my_type = data['database_connections'][my_db_key]['db_type']
    my_port = data['database_connections'][my_db_key]['port']
    return my_type, my_host, my_db, my_port, my_pw, my_user

def read_config_settings(excel_file_path):
    """
    Opens the specified Excel file and reads the [config] sheet.
    """
    df = pd.read_excel(excel_file_path, sheet_name='config')
    return df

def get_connection(db_name, schema_name):
    """
    Establishes a database connection using the provided database name and schema.
    """
    db_type, host, db, port, pw, user = get_conn_variables(db_name)
    conn_str = f"{db_type}://{user}:{pw}@{host}:{port}/{db}"
    engine = create_engine(conn_str)
    return engine.connect()

def validate_columns(table, xl_column_list, src_conn):
    """
    Validates the columns of the DataFrame against the database schema,
    returning the list of valid columns.
    """
    #   convert the list to a string for insertion into the query.
    xl_column_list = xl_column_list.iloc[:, 0].tolist()  # gets all values in the first column
    xl_column_string = ', '.join(str(val) for val in xl_column_list if pd.notnull(val))
    sql_validate_stmt = sql_validate_columns.replace('<<COLUMN_NAMES>>', xl_column_string)
    sql_validate_stmt = sql_validate_stmt.replace('<<TABLE_NAME>>', f'{table}')
    sql_validate_stmt = sql_validate_stmt.replace('\n', ' ')

    # print(sql_validate_stmt)
    try:
        df_db_columns = pd.read_sql(sql_validate_stmt, src_conn, )
    except Exception as e:
        logging.info(f'Trouble querying information_schema for columns.')
        logging.info(f'Error: \n=========\n{e}\n=========\n')
    db_column_list = df_db_columns['column_name'].tolist()

    ################################################################################
    #   Compare the two lists using set() then convert back to list.
    matched_set = (set(db_column_list) & set(xl_column_list))
    matches = [item for item in matched_set]
    naughty_list = []
    for column in xl_column_list:
        if column in matches:
            logging.info(f'  Matched: {column}')
        else:
            naughty_list.append(column)
            logging.info(f'Unmatched: {column}')
    logging.info(f'Column(s) not found in {sheet}:\n{naughty_list}')
    return(matches)

################################################################################
#   main code excution
if __name__ == "__main__":
    #   Initialization
    clear_screen()
    script_start = datetime.now()
    my_name = str(sys.argv[0])
    logging.info('='*80)
    logging.info(f'Hello - Starting: {my_name}')

################################################################################
# Get database settings
    settings_df = read_config_settings(excel_driver_location)
    logging.info(f'Config settings read from: {excel_driver_location}, getting connections.')

################################################################################
# get connections to source and dest
    logging.info(f'Getting connections for source database.')
    src_conn = get_connection(settings_df['Value'][0], settings_df['Value'][1])
    logging.info(f'Getting connections for destination database.')
    dest_conn = get_connection(settings_df['Value'][2], settings_df['Value'][3])
    logging.info(f'Connections established.')

################################################################################
# Open the xls workbook and get a list of tabs (tables to ETL) excluding config.
    workbook = pd.ExcelFile(excel_driver_location)
    sheet_names = workbook.sheet_names
    sheet_names = [name for name in sheet_names if name.lower() != 'config']
    # print(sheet_names)
    for sheet in sheet_names:
        logging.info(f'Processing sheet: {sheet}')
        df_column_list = pd.read_excel(excel_driver_location, sheet_name=sheet)
        good_list = validate_columns(sheet, df_column_list, src_conn)

################################################################################
# Build the query to get the good columns adding etl date/time as ETL_DATE_TIME_ZONE
        my_column_string = "'" + "', '".join(good_list) + "'"
        my_column_string += ', now() as ETL_DATE_TIME_ZONE'
        my_column_string = my_column_string.replace("'", "")
        my_query = sql_query_source.replace('<<COLUMN_NAMES>>', my_column_string)
        my_query = my_query.replace('<<TABLE_NAME>>', f'{sheet}')
        my_query = my_query.replace('\n', ' ')
        print(my_query)

################################################################################
# Query the data into a dataframe and write it to the destination database/schema.
        df_data = pd.read_sql(my_query, src_conn)
        df_data.to_sql(f'{sheet}', dest_conn, if_exists='replace', index=False)

################################################################################
#   Completion
    src_conn.close()  # Close the connection here
    dest_conn.close()  # Close the connection here
    script_end = datetime.now()
    runtime = str(script_end-script_start)
    logging.info(f'The time of execution of above program is :  {runtime}')
    logging.info(f'Goodbye - {my_name}')
    logging.info(f'='*80)