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

################################################################################
#   set up logging
log_file = str(sys.argv[0]).replace('.py', '.log')
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

def get_conn_variables(my_db):
    """
    This function reads the secrets file and returns the connection variables for Which_db
    """
    # Open and read the JSON file
    with open(secrets_location, 'r') as file:
        data = json.load(file)
    print(data)
    #   host, db, port, pw, user
    my_host = data['database_connections'][my_db]['host']
    my_db = data['database_connections'][my_db]['database']
    my_port = data['database_connections'][my_db]['port']
    my_pw = data['database_connections'][my_db]['password']
    my_user = data['database_connections'][my_db]['username']
    my_type = data['database_connections'][my_db]['db_type']
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

def read_secrets(db_name):
    """
    Opens the specified Excel file and returns a pandas DataFrame.
    """

################################################################################
#   main code excution
if __name__ == "__main__":
    #   Initialization
    clear_screen()
    script_start = datetime.now()
    my_name = str(sys.argv[0])
    logging.info('='*80)
    logging.info(f'Hello - Starting: {my_name}')
    # Get database settings
    settings_df = read_config_settings(excel_driver_location)
    print(settings_df)
    logging.info(f'Config settings read from: {excel_driver_location}, getting connections.')
    # get connections to source and dest
    # # Get source database connection
    print(settings_df['Value'][0])
    print(settings_df['Value'][1])
    print(settings_df['Value'][2])
    print(settings_df['Value'][3])
    src_conn = get_connection(settings_df['Value'][0], settings_df['Value'][1])
    dest_conn = get_connection(settings_df['Value'][2], settings_df['Value'][3])

    # src_host, src_db, src_port, src_pw, src_user = get_conn_variables('source_db')
    # logging.info(f'Source DB: {src_db} @ {src_host}:{src_port} as {src_user}')
    # # Get destination database connection variables
    # dest_host, dest_db, dest_port, dest_pw, dest_user = get_conn_variables('dest_db')
    # logging.info(f'Destination DB: {dest_db} @ {dest_host}:{dest_port} as {dest_user}')
