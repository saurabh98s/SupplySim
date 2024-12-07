import pandas as pd
import snowflake.connector
import os

def load_data():
    # Load data
    df = pd.read_csv('data/processed/transformed_data.csv')
    
    # Establish connection to Snowflake
    conn = snowflake.connector.connect(
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
        database=os.environ['SNOWFLAKE_DATABASE'],
        schema=os.environ['SNOWFLAKE_SCHEMA'],
        role=os.environ['SNOWFLAKE_ROLE']
    )
    
    # Write data to Snowflake
    success, nchunks, nrows, _ = df.to_sql('DAILY_DATA', conn, index=False, if_exists='replace', method='multi')
    print(f"Data loaded into Snowflake table 'DAILY_DATA': {nrows} rows.")

    conn.close()

if __name__ == '__main__':
    load_data()
