
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

read_file_path = "C:\\Users\\xuc\\dev\\ed-donner-agent\\agents\\rna_seq\\Muscle_kidney_tram_rapa_RNA_seq_count_data.csv"

organ_groups = ['Muscle', 'Kidney', 'Spleen']
treatments = ['Control', 'Rapamycin', 'Rapamycin/Trametinib', 'Trametinib']
genders = ['Male', 'Female']

# organ_groups = ['Muscle', 'Kidney']
# treatments = ['Control', 'Rapamycin']
# genders = ['Male', 'Female']



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

    # DEBUG: Limit to first 10 rows for faster debugging
    #df = df.head(10)

    # Skip the second row (index 1) only when it looks like a sample-label row.
    if len(df) > 1:
        second_row = df.iloc[1].astype(str)
        sample_like_count = second_row.str.contains(r"^\s*Sample\b", case=False, na=False).sum()

        # Drop only if multiple cells look like "Sample x" to avoid removing true gene rows.
        if sample_like_count >= max(2, len(df.columns) // 3):
            df = df.drop(index=1).reset_index(drop=True)
            print("Skipped second row (index 1) containing sample text labels.")
        else:
            print("Kept second row: it does not look like a sample-label row.")

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
    
    # Apply log2 transformation to expression columns (sample columns)
    import numpy as np

    print("\nApplying log2 transformation to all numeric data points...")
    expression_col_indices = sorted({idx for cols in sample_groups.values() for idx in cols})
    expression_columns = df.columns[expression_col_indices]

    # Convert expression columns to numeric. Label rows like "Sample x" become NaN.
    for col in expression_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Apply log2 to each expression column and replace original values
    for col in expression_columns:
        # Add a small pseudocount (e.g., 1) to avoid log2(0) = -inf
        df[col] = np.log2(df[col] + 1)
    
    print(f"Log2 transformation applied to {len(expression_columns)} expression columns.")
    print("\nFirst few rows after log2 transformation:")
    print(df.head())
    
    # Save the transformed data to a new file
    output_file_path = os.path.splitext(read_file_path)[0] + "_log2.csv"
    df.to_csv(output_file_path, index=False)
    print(f"\nTransformed data saved to: {output_file_path}")

    # For t-tests, skip rows that contain sample label text (for example, "Sample x").
    gene_id_col = df.columns[0]
    ttest_df = df[~df[gene_id_col].astype(str).str.contains(r"^\s*Sample\b", case=False, na=False)].copy().reset_index(drop=True)
    skipped_rows = len(df) - len(ttest_df)
    print(f"Rows skipped for t-test due to sample labels: {skipped_rows}")
    
    # Build one summary CSV with requested columns per organ+treatment.
    from scipy.stats import ttest_ind

    print("\n" + "="*80)
    print("Building summary metrics by organ and treatment...")
    print("="*80)

    summary_results = []

    for organ in organ_groups:
        print(f"\nProcessing organ: {organ}")
        for treatment in treatments:
            male_group_name = f"Male {organ} {treatment} Biol"
            female_group_name = f"Female {organ} {treatment} Biol"
            male_control_name = f"Male {organ} Control Biol"
            female_control_name = f"Female {organ} Control Biol"

            if male_group_name not in sample_groups or female_group_name not in sample_groups:
                print(f"  Warning: Missing treatment groups for {organ} / {treatment}. Skipping...")
                continue

            male_cols = sample_groups[male_group_name]
            female_cols = sample_groups[female_group_name]
            male_control_cols = sample_groups.get(male_control_name, [])
            female_control_cols = sample_groups.get(female_control_name, [])

            # Keep rows where all required treatment columns are numeric.
            required_treatment_cols = male_cols + female_cols
            comp_df = ttest_df[
                ttest_df.iloc[:, required_treatment_cols].notna().all(axis=1)
            ].reset_index(drop=True)

            # Compute per-gene treatment means in log2 space.
            male_avg = comp_df.iloc[:, male_cols].mean(axis=1)
            female_avg = comp_df.iloc[:, female_cols].mean(axis=1)

            # Treatment vs control ratios for each gender.
            male_control_avg = comp_df.iloc[:, male_control_cols].mean(axis=1) if male_control_cols else pd.Series(np.nan, index=comp_df.index)
            female_control_avg = comp_df.iloc[:, female_control_cols].mean(axis=1) if female_control_cols else pd.Series(np.nan, index=comp_df.index)
            
            male_log2_ratio_treatment_vs_control = male_avg / male_control_avg.replace(0, np.nan)
            female_log2_ratio_treatment_vs_control = female_avg / female_control_avg.replace(0, np.nan)

            male_p_values = []
            female_p_values = []

            for idx in range(len(comp_df)):
                # Male treatment vs male control p-value.
                if male_control_cols:
                    male_control_values = comp_df.iloc[idx, male_control_cols].values.astype(float)
                    male_treatment_values = comp_df.iloc[idx, male_cols].values.astype(float)
                    _, male_p = ttest_ind(male_control_values, male_treatment_values, equal_var=False)
                else:
                    male_p = np.nan

                # Female treatment vs female control p-value.
                if female_control_cols:
                    female_control_values = comp_df.iloc[idx, female_control_cols].values.astype(float)
                    female_treatment_values = comp_df.iloc[idx, female_cols].values.astype(float)
                    _, female_p = ttest_ind(female_control_values, female_treatment_values, equal_var=False)
                else:
                    female_p = np.nan

                male_p_values.append(male_p)
                female_p_values.append(female_p)

            treatment_summary = pd.DataFrame({
                gene_id_col: comp_df[gene_id_col].values,
                'organ': organ,
                'treatment': treatment,
                'male_avg': male_avg.values,
                'female_avg': female_avg.values,
                'male_p_value_vs_control': male_p_values,
                'female_p_value_vs_control': female_p_values,
                'male_ratio_treatment_vs_control': male_log2_ratio_treatment_vs_control.values,
                'female_ratio_treatment_vs_control': female_log2_ratio_treatment_vs_control.values,
            })

            summary_results.append(treatment_summary)
            print(f"  Added {len(treatment_summary)} rows for {organ} / {treatment}")

    if summary_results:
        summary_df = pd.concat(summary_results, ignore_index=True)
        summary_df = summary_df.sort_values(
            by=['organ', 'treatment', gene_id_col],
            kind='mergesort'
        ).reset_index(drop=True)

        # Pivot to wide format: one gene per row, organ+treatment in columns.
        metric_columns = [
            'male_avg',
            'female_avg',
            'male_p_value_vs_control',
            'female_p_value_vs_control',
            'male_ratio_treatment_vs_control',
            'female_ratio_treatment_vs_control',
        ]

        wide_multi = summary_df.pivot_table(
            index=gene_id_col,
            columns=['organ', 'treatment'],
            values=metric_columns,
            aggfunc='first'
        )

        # Reorder to Organ -> Treatment -> Metric for readable grouped columns.
        wide_multi = wide_multi.reorder_levels([1, 2, 0], axis=1).sort_index(axis=1)

        # For Control groups, keep only average columns.
        control_metrics_to_drop = {
            'male_p_value_vs_control',
            'female_p_value_vs_control',
            'male_ratio_treatment_vs_control',
            'female_ratio_treatment_vs_control',
        }
        kept_columns = [
            col for col in wide_multi.columns
            if not (col[1] == 'Control' and col[2] in control_metrics_to_drop)
        ]
        wide_multi = wide_multi.loc[:, kept_columns]

        # Reorder columns: male before female, then avg, p_value, ratio per gender per treatment.
        col_order = []
        for organ in organ_groups:
            for treatment in treatments:
                for gender in ['Male', 'Female']:
                    gender_prefix = gender.lower()
                    
                    # Add avg column
                    avg_col = f"{gender_prefix}_avg"
                    if (organ, treatment, avg_col) in wide_multi.columns:
                        col_order.append((organ, treatment, avg_col))
                    
                    # Add p_value column (only for non-Control treatments)
                    if treatment != 'Control':
                        p_col = f"{gender_prefix}_p_value_vs_control"
                        if (organ, treatment, p_col) in wide_multi.columns:
                            col_order.append((organ, treatment, p_col))
                        
                        # Add ratio column
                        ratio_col = f"{gender_prefix}_ratio_treatment_vs_control"
                        if (organ, treatment, ratio_col) in wide_multi.columns:
                            col_order.append((organ, treatment, ratio_col))
        
        wide_multi = wide_multi.loc[:, col_order]

        # Flatten multi-index columns into: Organ_Treatment_Metric
        wide_df = wide_multi.copy()
        wide_df.columns = [f"{organ}_{treatment}_{metric}" for organ, treatment, metric in wide_df.columns]

        wide_df = wide_df.reset_index().sort_values(by=[gene_id_col], kind='mergesort').reset_index(drop=True)
        
        # Add empty columns between treatment groups for visual separation
        new_cols_with_separators = [gene_id_col]
        current_organ = None
        current_treatment = None
        sep_count = 0
        
        for col in wide_df.columns[1:]:  # Skip gene_id_col
            parts = col.split('_')
            if len(parts) >= 2:
                col_organ = parts[0]
                col_treatment = parts[1]
                
                # Add separator column when treatment changes (organ or treatment)
                if current_organ is not None and (col_organ != current_organ or col_treatment != current_treatment):
                    new_cols_with_separators.append(f"_sep_{sep_count}")
                    sep_count += 1
                
                current_organ = col_organ
                current_treatment = col_treatment
            
            new_cols_with_separators.append(col)
        
        # Create new dataframe with separator columns
        sep_columns = [c for c in new_cols_with_separators if c.startswith('_sep_')]
        for sep_col in sep_columns:
            wide_df[sep_col] = ''
        
        # Reorder to match the new column order
        wide_df = wide_df[new_cols_with_separators]

        # Build metadata aligned to the final wide_df column order (including separators).
        flat_to_tuple = {
            f"{organ}_{treatment}_{metric}": (organ, treatment, metric)
            for organ, treatment, metric in wide_multi.columns
        }
        excel_col_meta = []
        for col in wide_df.columns[1:]:
            if col in sep_columns:
                excel_col_meta.append(None)
            else:
                excel_col_meta.append(flat_to_tuple.get(col))

        # Keep separator positions for Excel formatting, then blank their CSV headers.
        sep_col_positions = [idx for idx, col in enumerate(wide_df.columns) if col in sep_columns]
        wide_df = wide_df.rename(columns={sep_col: '' for sep_col in sep_columns})

        csv_output_path = os.path.splitext(read_file_path)[0] + "_organ_treatment_gender_summary_wide.csv"
        wide_df.to_csv(csv_output_path, index=False)
        print(f"\nWide summary CSV saved to: {csv_output_path}")

        # Export Excel with merged headers by organ and treatment/control groups.
        excel_output_path = os.path.splitext(read_file_path)[0] + "_organ_treatment_gender_summary_wide.xlsx"
        try:
            with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Analysis Results')
                writer.sheets['Analysis Results'] = worksheet

                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                subheader_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#D9E1F2',
                    'border': 1
                })
                metric_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#EEF3FA',
                    'border': 1
                })
                text_format = workbook.add_format({'border': 1, 'align': 'left'})
                num_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '0.0000'})

                # Write data body (no header) starting on row 4 so rows 1-3 are merged headers.
                wide_df.to_excel(writer, sheet_name='Analysis Results', startrow=3, index=False, header=False)

                # First column (gene id) spans all 3 header rows.
                worksheet.merge_range(0, 0, 2, 0, gene_id_col, header_format)

                # Row 3 (index 2): metric labels aligned to final columns (blank for separators).
                for i, meta in enumerate(excel_col_meta, start=1):
                    if meta is None:
                        worksheet.write_blank(2, i, None, metric_format)
                    else:
                        worksheet.write(2, i, meta[2], metric_format)

                # Row 1 (index 0): organ merged blocks, skipping separator columns.
                idx = 0
                while idx < len(excel_col_meta):
                    meta = excel_col_meta[idx]
                    if meta is None:
                        worksheet.write_blank(0, idx + 1, None, header_format)
                        idx += 1
                        continue

                    organ = meta[0]
                    end_idx = idx
                    while end_idx + 1 < len(excel_col_meta):
                        next_meta = excel_col_meta[end_idx + 1]
                        if next_meta is None or next_meta[0] != organ:
                            break
                        end_idx += 1

                    if end_idx == idx:
                        worksheet.write(0, idx + 1, organ, header_format)
                    else:
                        worksheet.merge_range(0, idx + 1, 0, end_idx + 1, organ, header_format)
                    idx = end_idx + 1

                # Row 2 (index 1): treatment/control merged blocks, skipping separator columns.
                idx = 0
                while idx < len(excel_col_meta):
                    meta = excel_col_meta[idx]
                    if meta is None:
                        worksheet.write_blank(1, idx + 1, None, subheader_format)
                        idx += 1
                        continue

                    organ, treatment, _ = meta
                    end_idx = idx
                    while end_idx + 1 < len(excel_col_meta):
                        next_meta = excel_col_meta[end_idx + 1]
                        if next_meta is None or next_meta[0] != organ or next_meta[1] != treatment:
                            break
                        end_idx += 1

                    if end_idx == idx:
                        worksheet.write(1, idx + 1, treatment, subheader_format)
                    else:
                        worksheet.merge_range(1, idx + 1, 1, end_idx + 1, treatment, subheader_format)
                    idx = end_idx + 1

                # Apply cell formats to data region.
                for r in range(3, 3 + len(wide_df)):
                    worksheet.write(r, 0, wide_df.iloc[r - 3, 0], text_format)
                    for c in range(1, wide_df.shape[1]):
                        val = wide_df.iloc[r - 3, c]
                        
                        # Skip separator columns and empty values
                        if c in sep_col_positions or pd.isna(val) or (isinstance(val, str) and val == ''):
                            worksheet.write_blank(r, c, None, text_format)
                        else:
                            worksheet.write(r, c, float(val), num_format)

                worksheet.set_column(0, 0, 24)
                worksheet.set_column(1, wide_df.shape[1] - 1, 18)
                worksheet.freeze_panes(3, 1)

            print(f"Merged-header Excel saved to: {excel_output_path}")
        except (ImportError, ModuleNotFoundError):
            print("xlsxwriter is not available; merged-cell Excel export was skipped.")
    else:
        print("No summary rows were generated; CSV file was not created.")


    

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



