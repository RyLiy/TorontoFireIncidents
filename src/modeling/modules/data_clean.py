import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import numpy as np
from sklearn.impute import KNNImputer

class DataCleaner:

    CATEGORICAL_COLUMNS = ['Area_of_Origin','Building_Status','Business_Impact','Extent_Of_Fire','Final_Incident_Type',
'Fire_Alarm_System_Impact_on_Evacuation','Fire_Alarm_System_Operation','Fire_Alarm_System_Presence',
'Ignition_Source','Material_First_Ignited','Method_Of_Fire_Control','Possible_Cause',
'Property_Use','Smoke_Alarm_at_Fire_Origin','Smoke_Alarm_at_Fire_Origin_Alarm_Failure','Smoke_Alarm_at_Fire_Origin_Alarm_Type',
'Smoke_Alarm_Impact_on_Persons_Evacuating_Impact_on_Evacuation','Smoke_Spread','Sprinkler_System_Operation','Sprinkler_System_Presence',
'Status_of_Fire_On_Arrival','Exposures', 'Incident_Ward']
        
    COLUMNS_TO_KEEP = ['Area_of_Origin', 'Building_Status', 'Business_Impact', 'Extent_Of_Fire', 'Final_Incident_Type', 
                    'Fire_Alarm_System_Impact_on_Evacuation', 'Fire_Alarm_System_Operation', 'Fire_Alarm_System_Presence', 
                    'Ignition_Source', 'Initial_CAD_Event_Type', 'Material_First_Ignited', 'Method_Of_Fire_Control', 
                    'Possible_Cause', 'Property_Use', 'Smoke_Alarm_at_Fire_Origin', 'Smoke_Alarm_at_Fire_Origin_Alarm_Failure', 
                    'Smoke_Alarm_at_Fire_Origin_Alarm_Type', 'Smoke_Alarm_Impact_on_Persons_Evacuating_Impact_on_Evacuation', 
                    'Smoke_Spread', 'Sprinkler_System_Operation', 'Sprinkler_System_Presence', 'Status_of_Fire_On_Arrival']


    # List of columns to remove
    COLUMNS_TO_REMOVE = [
        '_id','Exposures','Ext_agent_app_or_defer_time', 'Fire_Under_Control_Time', 'Incident_Number', 
        'Incident_Station_Area', 'Intersection', 'Last_TFS_Unit_Clear_Time', 
        'Latitude', 'Longitude', 'TFS_Alarm_Time', 'TFS_Arrival_Time','Level_Of_Origin'
    ]

    @staticmethod
    def createPipeline(df):
        categorical_column_imputer = Pipeline(steps=[
            ('imputer0', KNNImputer())
        ])
        # Get the categorical columns by index numbers
        c_idx = [df.columns.get_loc(item) for item in DataCleaner.COLUMNS_TO_KEEP]

        missing_value_imputer = ColumnTransformer(transformers=[
                                                        ('imputer', categorical_column_imputer, c_idx)
                                                    ])

        # Feed the categorical columns into the simple imputer pipeline
        missing_value_imputer = ColumnTransformer(transformers=[
            ('categorical_imputer', categorical_column_imputer, c_idx),
            #('numerical_imputer', categorical_column_imputer, c_idx)
            ])
        

        
        return missing_value_imputer

    @staticmethod
    def cleanse_dataframe(df):
        
        pd.set_option('display.max_columns', None)

        # Remove columns from the DataFrame
        df.drop(columns=DataCleaner.COLUMNS_TO_REMOVE, inplace=True)

        # # Remove non-numeric characters -- Should be encoded as part of the pipeline!
        # df_cleaned = df[:]
        # for col in DataCleaner.COLUMNS_TO_KEEP:
        #     df_cleaned[col] = df_cleaned[col].replace('[^0-9]', '', regex=True)

        # Replace empty strings with pd.NA (NaN)
        df_cleaned = df.mask(df == '', pd.NA)

        # Removing rows with no values at all according to column name: Area_of_Origin
        # To remove rows with missing values in a specific column(s)
        df_cleaned = df_cleaned.dropna(subset=['Area_of_Origin', 'Initial_CAD_Event_Type'])

        # Removing alse positives.
        df_cleaned = df_cleaned[df_cleaned['Final_Incident_Type'] != "03 - NO LOSS OUTDOOR fire (exc: Sus.arson,vandal,child playing,recycling or dump fires)"]

        # Converting categorical columns to string to ensure data integrity, ease the imputation process, and making the dataset ready for subsequent analysis
        for col in DataCleaner.COLUMNS_TO_KEEP:
            df_cleaned.loc[:, col] = df_cleaned[col].astype('object')  # Cast to object dtype first
            df_cleaned.loc[:, col] = df_cleaned[col].astype('string')  # Then convert to string

        # Remove outliers based on response_variable, Estimated_Dollar_Loss. using z-score method, elimate rows 3 standard deviations from the mean.
        z_scores = df_cleaned['Estimated_Dollar_Loss'].apply(lambda x: (x - df_cleaned['Estimated_Dollar_Loss'].mean()) / df_cleaned['Estimated_Dollar_Loss'].std())
        df_cleaned = df_cleaned[(z_scores < 3) & (z_scores > -3)]  # Adjust threshold as needed

        # Replace all NAType values with NaN, or skLearn won't recognize it.
        df_cleaned.replace('NAType', np.nan)

        return df_cleaned
