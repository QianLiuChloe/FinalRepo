import pandas as pd


df1 = pd.read_excel('[0, 38, 1066, 420]_0_size.xlsx')  # Table1
df2 = pd.read_excel('1_category_counts.xlsx')  # Table2


df2.iloc[:, 0] = df2.iloc[:, 0].str.upper()


quantity_dict = df2.groupby(df2.columns[0])[df2.columns[1]].sum().to_dict()


df1['Number'] = 0


for idx, row in df1.iterrows():
    component_name = row[df1.columns[0]].upper()

    if component_name in quantity_dict:
        df1.at[idx, 'Number'] = quantity_dict[component_name]


df1.to_excel('merged_table.xlsx', index=False)
