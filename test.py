import pandas as pd


data = {
    'MARK': [1, 2, 3],
    'TYPE': ['A', 'B', 'C'],
    'SIZE (MINIMUM)': [10, 20, 30],
    'REINFORCEMENT': [True, False, True]
}


df = pd.DataFrame(data)


print("DataFrame 列名:")
print(df.columns)


matching_columns = [col for col in df.columns if 'SIZE' in col.upper()]


print("匹配的列名列表:")
print(matching_columns)

if matching_columns:
    size_col_name = matching_columns[0]
    print(f"列名包含 'SIZE' 的列是: {size_col_name}")
else:
    print("没有找到包含 'SIZE' 的列名。")