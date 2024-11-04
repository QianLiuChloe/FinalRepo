import pandas as pd


data = {
    'MARK': [1, 2, 3],
    'TYPE': ['A', 'B', 'C'],
    'SIZE (MINIMUM)': [10, 20, 30],
    'REINFORCEMENT': [True, False, True]
}


df = pd.DataFrame(data)


print("DataFrame column name:")
print(df.columns)


matching_columns = [col for col in df.columns if 'SIZE' in col.upper()]


print("List of matching column names:")
print(matching_columns)

if matching_columns:
    size_col_name = matching_columns[0]
    print(f"The columns containing ‘SIZE’ are: {size_col_name}")
else:
    print("No column name containing ‘SIZE’ was found.")