import pandas as pd
import re
import math


def convert_to_uppercase(df):
    """Convert all non-empty cells in the dataframe to uppercase strings."""
    df = df.applymap(lambda x: str(x).upper() if pd.notnull(x) else x)
    return df


def find_size_row(df):
    """Find the first row that contains 'SIZE' and return a new dataframe starting from that row."""
    for index, row in df.iterrows():
        if row.str.contains('SIZE', case=False, na=False).any():
            return df.iloc[index:].reset_index(drop=True)
    return df


def extract_size_elements(size_str):
    """Extract numbers and special characters like SQ and DIA from the size string."""
    size_str = size_str.upper()
    # Extract numbers and special keywords (SQ, DIA)
    elements = re.findall(r'\d+|SQ|DIA', size_str)
    return elements


def create_new_columns(df, size_col_name):
    """Create new columns based on the extracted size elements."""
    size_data = df[size_col_name].dropna().apply(extract_size_elements)

    # Find the maximum number of numeric elements in any row
    max_size = size_data.apply(lambda x: len([e for e in x if e.isdigit()])).max()

    # Create new SIZE columns
    for i in range(1, max_size + 1):
        df[f'SIZE{i}'] = size_data.apply(lambda x: x[i - 1] if i - 1 < len(x) and x[i - 1].isdigit() else None)

    return df


def calc_for_row(elements):
    """Perform calculations based on the extracted size elements."""
    if 'SQ' in elements:
        idx = elements.index('SQ')
        if idx == 0:  # SQ is the first element
            num = int(elements[idx + 1])
            other_nums = [int(e) for e in elements[idx + 2:] if e.isdigit()]
            return num * num * math.prod(other_nums) if other_nums else num * num
        else:  # SQ is not the first element
            num = int(elements[idx - 1])
            other_nums = [int(e) for e in elements[:idx - 1] + elements[idx + 1:] if e.isdigit()]
            return num * num * math.prod(other_nums) if other_nums else num * num

    elif 'DIA' in elements:
        idx = elements.index('DIA')
        if idx == 0:  # DIA is the first element
            num = int(elements[idx + 1])
            other_nums = [int(e) for e in elements[idx + 2:] if e.isdigit()]
            return 0.25 * num * num * math.pi * math.prod(other_nums) if other_nums else 0.25 * num * num * math.pi
        else:  # DIA is not the first element
            num = int(elements[idx - 1])
            other_nums = [int(e) for e in elements[:idx - 1] + elements[idx + 1:] if e.isdigit()]
            return 0.25 * num * num * math.pi * math.prod(other_nums) if other_nums else 0.25 * num * num * math.pi

    else:
        # If only numbers, return their product
        nums = [int(e) for e in elements if e.isdigit()]
        return math.prod(nums) if nums else None


def calculate(df, size_col_name):
    """Perform calculations for each row in the dataframe based on the size column."""
    df['Calculation'] = df[size_col_name].dropna().apply(lambda x: calc_for_row(extract_size_elements(x)))
    return df


def process_excel(file_path, output_file):
    infos = []
    """Main function to process the Excel file and save the results."""
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Step 1: Convert all non-empty cells to uppercase
    df = convert_to_uppercase(df)

    # Step 2: Find the first row that contains "SIZE"
    df = find_size_row(df)

    # Step 3: Create new columns based on the extracted size elements
    try:
        size_col_name = [col for col in df.columns if 'SIZE' in col.upper()][0]
    except:
        size_col_name = df.columns[df.apply(lambda x: x.str.contains('SIZE',case=False, na=False)).any()].tolist()[0]
     

    df = create_new_columns(df, size_col_name)

    # Step 4: Calculate values for the new "Calculation" column
    df = calculate(df, size_col_name)

    # Save the processed data to a new Excel file
    output_file = output_file
    df.to_excel(output_file, index=False)
    infos.append(f"Processed file saved as {output_file}")
    print(f"Processed file saved as {output_file}")
    return infos
