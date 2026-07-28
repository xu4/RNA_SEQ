
import pandas as pd
import os

def convert_xlsx_to_csv(xlsx_path, csv_path):
    """
    Converts an XLSX file to a CSV file.

    Args:
        xlsx_path (str): The path to the input XLSX file.
        csv_path (str): The path to the output CSV file.
    """
    try:
        df = pd.read_excel(xlsx_path)
        df.to_csv(csv_path, index=False)
        print(f"Successfully converted '{xlsx_path}' to '{csv_path}'")
        return True
    except FileNotFoundError:
        print(f"Error: The XLSX file '{xlsx_path}' was not found.")
        return False
    except Exception as e:
        print(f"An error occurred during XLSX to CSV conversion: {e}")
        return False

# Specify the path to your input file (can be XLSX or CSV)
# input_file_path = "C:\\Users\\gan88\\Downloads\\Muscle_kidney_tram_rapa_RNA_seq_count_data.xlsx" # Change this to your input file
# output_csv_file_path = os.path.splitext(input_file_path)[0] + ".csv" # Generate CSV path from input

# df = None
# if input_file_path.lower().endswith(".xlsx"):
#     print(f"Attempting to convert XLSX file: {input_file_path}")
#     if convert_xlsx_to_csv(input_file_path, output_csv_file_path):
#         read_file_path = output_csv_file_path
#     else:
#         print("XLSX to CSV conversion failed. Exiting.")
#         exit() # Exit if conversion fails
# elif input_file_path.lower().endswith(".csv"):
#     read_file_path = input_file_path
# else:
#     print("Error: Unsupported file format. Please provide an .xlsx or .csv file.")
#     exit()

read_file_path = "C:\\Users\\gan88\\Downloads\\Muscle_kidney_tram_rapa_RNA_seq_count_data.csv"


try:
    if read_file_path.lower().endswith(".csv"):
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(read_file_path)
        #print("\nColumn names in the CSV file:")
    else:
        # This part should ideally not be reached if the above logic works
        # It's here as a fallback in case read_file_path is not a CSV for some reason
        df = pd.read_excel(read_file_path) # Attempt to read as excel if it was not converted
        #print("\nColumn names in the Excel file:")

    # for column in df.columns:
    #     print(column)

    # Create a dictionary to store column numbers for each labeled group
    sample_groups = {}

    # Define patterns or keywords to identify each group.
    # This is a critical step and needs to be adapted based on your actual column naming convention.
    # For example, if your column names are 'Male_Muscle_Rapamycin_Biol_1', 'Male_Muscle_Rapamycin_Biol_2', etc.
    # You would adjust the patterns accordingly.

    # --- EXAMPLE PATTERNS (YOU WILL NEED TO CUSTOMIZE THESE) ---
    # These are example patterns. You should inspect your actual column names
    # and define patterns that accurately capture your desired groups.
    # For instance, if a column name 'Male_Muscle_Rapamycin_Biol_A' should belong to 'Male Muscle Rapamycin Biol',
    # the pattern 'Male Muscle Rapamycin Biol' should match it.
    # You might need to use regular expressions for more complex patterns.

    organ_groups = ['Muscle', 'Kidney', 'Spleen']
    treatments = ['Control', 'Rapamycin', 'Rapamycin/Trametinib', 'Trametinib']
    genders = ['Male', 'Female']

    group_patterns = {}
    for gender in genders:
        for organ_group in organ_groups:
            for treatment in treatments:
                # Assuming the column names follow a pattern like "Gender OrganGroup Treatment Biol"
                # You may need to adjust this string concatenation based on your actual column names.
                # For example, if it's "Male_Muscle_Rapamycin_Biol", you might need f"{gender}_{organ_group}_{treatment}_Biol"
                # The current pattern assumes spaces.
                label = f"{gender} {organ_group} {treatment} Biol"
                #print(label)
                group_patterns[label] = [label] # The pattern to match is the full label itself

    # ...existing code...
    # Iterate through the columns of the DataFrame and populate the sample_groups dictionary
        # Add more groups and their corresponding patterns as needed


    # Iterate through the columns of the DataFrame and populate the sample_groups dictionary
    print("\nMapping columns to sample groups:")
    for col_num, column_name in enumerate(df.columns):
        #print(f"{col_num}: {column_name}")
        assigned_to_group = False
        for group_label, patterns in group_patterns.items():
            for pattern in patterns:
                if pattern in column_name: # Simple substring match
                    if group_label not in sample_groups:
                        sample_groups[group_label] = []
                    sample_groups[group_label].append(col_num)
                    #print(f"  Column '{column_name}' (Index: {col_num}) assigned to '{group_label}'")
                    assigned_to_group = True
                    break # Move to the next column after assignment
            if assigned_to_group:
                break
        if not assigned_to_group:
            print(f"  Column '{column_name}' (Index: {col_num}) did not match any defined group.")

    print("\nSample Groups Dictionary:")
    for group, columns in sample_groups.items():
        print(f"'{group}': {columns}")
    
    

except FileNotFoundError:
    print(f"Error: The file '{read_file_path}' was not found. Please check the path.")
except UnicodeDecodeError as e:
    print(f"Error: A UnicodeDecodeError occurred while reading the file '{read_file_path}'.")
    print(f"Encoding tried: {e.encoding}")
    print(f"Reason: {e.reason}")
    print(f"Character in error: {repr(e.object[e.start:e.end])} at position {e.start}")
    print("This might be due to special characters in the file content or an incompatible file format.")
    print("Consider specifying the correct encoding, e.g., df = pd.read_csv(csv_file_path, encoding='latin1').")
    print("You can also try opening the CSV file in a text editor like VS Code and check the encoding (bottom right corner) or look for unusual characters.")
    print(f"An unexpected error occurred: {e}")



