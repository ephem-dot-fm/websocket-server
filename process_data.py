from psycopg2 import sql
from helper_functions import connect_to_pg_dataframe
import pandas as pd
import time


# Temporary holder will hold 4 at a time
temp_audio_values = pd.DataFrame(columns= ['station', 'timestamp_unix', 'tempo', 'loudness', 'pitch'])
cumulative_audio_values = temp_audio_values.copy()

def remove_outlier_IQR(df):
    Q1=df.quantile(0.25)
    Q3=df.quantile(0.75)
    IQR=Q3-Q1
    df_final=df[~((df<(Q1-1.5*IQR)) | (df>(Q3+1.5*IQR)))]
    return df_final

    
# Weed out outliers, then find mean and convert to colors for front end
def process_audio_data(data):
    # reference the value temp_audio_values
    global temp_audio_values

    # add new row
    new_row = pd.DataFrame(data={
        'station': data['station'], 
        'timestamp_unix': time.time(),
        'tempo' : data['tempo'],
        'loudness': data['loudness'], 
        'pitch' : data['pitch'],
        }, 
        index = ['station'], 
        columns = ['station', 'timestamp_unix', 'tempo', 'loudness', 'pitch']
        )
    
    temp_audio_values = pd.concat([temp_audio_values, new_row], ignore_index = True)

    # create mask to separate out audio values from one station only
    station_mask = temp_audio_values['station'] == data['station']
    station_vals = temp_audio_values[station_mask]

    # process once there are 4 cumulative
    if len(temp_audio_values[station_mask].index) == 4:
        # Create a new DataFrame cleansed of outliers
        station_vals[['tempo','loudness', 'pitch']] = station_vals.loc[:, ['tempo','loudness', 'pitch']].apply(func = remove_outlier_IQR)
        station_vals = station_vals.fillna(0)


        # Writing the cleansed values to Postgres database
        conn = connect_to_pg_dataframe()
        station_vals.to_sql('audio_lake', conn, if_exists='append', index=False)
        conn.close()


        # Add new values to cumulative holder
        global cumulative_audio_values
        cumulative_audio_values = pd.concat([cumulative_audio_values, station_vals], ignore_index = True)
        print(f'Cumulative audio values are now\n{cumulative_audio_values}')
        
        # TODO Write to sqlite3


        # Drop those rows that match the station which has 4 values in it
        temp_audio_values = temp_audio_values[temp_audio_values.station != data['station']]

    elif len(temp_audio_values[station_mask].index) > 4:
        print("The DataFrame has more than 4 rows for one station!")

def process(data):
    if [*data][0] == 'audio_values':
        results = process_audio_data(data['audio_values'])

if __name__=="__main__":
    # Mock dataset to test with
    new_rows = [
        {
        'station': 'ddr', 
        'tempo' : 100,
        'loudness': 100, 
        'pitch' : 100,
        },

        {
        'station': 'ddr', 
        'tempo' : 102,
        'loudness': 102, 
        'pitch' : 102,
        },

        {
        'station': 'ddr', 
        'tempo' : 116,
        'loudness': 116, 
        'pitch' : 116,
        },

        {
        'station': 'ddr', 
        'tempo' : 104,
        'loudness': 104, 
        'pitch' : 104,
        },

        {
        'station': 'ddr', 
        'tempo' : 108,
        'loudness': 108, 
        'pitch' : 108,
        },

        {
        'station': 'ddr', 
        'tempo' : 112,
        'loudness': 112, 
        'pitch' : 112,
        },

        {
        'station': 'ddr', 
        'tempo' : 114,
        'loudness': 117, 
        'pitch' : 200,
        },
        
        {
        'station': 'ddr', 
        'tempo' : 200,
        'loudness': 200, 
        'pitch' : 200,
        }
    ]

    # Create a df with 8 rows to experiment with
    for row in new_rows:
        process_audio_data(row)

    # Remove outliers
    # print(together_df[['tempo', 'loudness', 'pitch']].apply(remove_outlier_IQR))
