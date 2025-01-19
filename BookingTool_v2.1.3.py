import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def process_data():
    val_dev = int(device_id_entry.get())

    try:
        val_file2 = log_file
        val_file1 = data_file
        replace_file_path = replace_file

        # Read file1 as CSV with UTF-8 encoding and ; as delimiter
        file1 = pd.read_csv(val_file1, delimiter=';', encoding='utf-8', quotechar='"')

        # Read file2 as TXT file, specifying column names and using only the first 5 columns
        file2 = pd.read_csv(
            val_file2,
            delimiter='\t',
            header=None,
            encoding='utf-8',
            quotechar='"',
            names=['col1', 'accountnumber', 'id', 'timestamp', 'col5'],
            usecols=[0, 1, 2, 3, 4]
        )

        # Handle non-finite values and convert 'mitarbeiternummer' to integer
        file1['mitarbeiternummer'].fillna(0, inplace=True)  # Replace NaN with 0
        file1['mitarbeiternummer'] = file1['mitarbeiternummer'].astype(int)  # Convert to integer

        # Remove unnecessary columns from file1 and file2
        columns_keep = ['id', 'mitarbeiternummer']
        file1 = file1[columns_keep]

        del file2["col1"]
        del file2["col5"]

        # Filter out rows where 'accountnumber' is greater or equal to 200
        filtered_col = file2[file2['accountnumber'] < 200]

        # Read the replace file
        replace_file_df = pd.read_csv(replace_file_path, delimiter=';', encoding='utf-8', quotechar='"')

        # Keep only relevant columns from the replace file
        replace_file_df = replace_file_df[['aktionsnummer', 'devicenummer', 'satzart']]

        # Filter replace file rows by the device number that matches the entered Device ID
        relevant_replacements = replace_file_df[replace_file_df['devicenummer'] == val_dev]

        # Replace values in 'accountnumber' based on 'aktionsnummer' and 'satzart'
        replacements = dict(zip(relevant_replacements['satzart'], relevant_replacements['aktionsnummer']))
        filtered_col['accountnumber'].replace(replacements, inplace=True)

        # Merge data based on 'id' field
        output1 = pd.merge(filtered_col, file1, on='id', how='left')
        output1.drop(columns=['id'], inplace=True)

        # Add 'devicenumber' column with the same value as the entered Device ID
        num_rows = output1.shape[0]
        variables = [val_dev] * num_rows
        output1['devicenumber'] = variables

        # Reorder columns
        new_output_order = ['mitarbeiternummer', 'timestamp', 'accountnumber', 'devicenumber']
        output1 = output1[new_output_order]

        # Rename column for employee
        output1.rename(columns={'mitarbeiternummer': 'employee'}, inplace=True)

        output1['employee'] = output1['employee'].fillna("").astype(str)

        # Convert all numeric columns with integer values from float to int
        for col in output1.select_dtypes(include=['float']).columns:
            if (output1[col] % 1 == 0).all():  # Check if all values are whole numbers
                output1[col] = output1[col].astype(int)

        # Save the output as a CSV file with UTF-8 encoding
        output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if output_file:
            output1.to_csv(output_file, index=False, encoding='utf-8', sep=';', quotechar='"')
            messagebox.showinfo("Success", "Data processing completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def merge_files():
    try:
        global merged_data
        files = filedialog.askopenfilenames(title="Select CSV Files to Merge", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if files:
            merged_data = pd.DataFrame()
            for file in files:
                df = pd.read_csv(file, delimiter=';', encoding='utf-8', quotechar='"')
                merged_data = pd.concat([merged_data, df], ignore_index=True)

            output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
            if output_file:
                merged_data.to_csv(output_file, index=False, encoding='utf-8', sep=';', quotechar='"')
                messagebox.showinfo("Success", f"Files merged successfully and saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def show_create_output_page():
    create_output_frame.tkraise()

def show_merge_outputs_page():
    merge_outputs_frame.tkraise()

def show_main_menu_page():
    main_menu_frame.tkraise()

def select_file(file_type):
    global log_file, data_file, replace_file
    selected_file = filedialog.askopenfilename(title=f"Select {file_type.capitalize()} File", filetypes=(("All files", "*.*"),))
    if file_type == 'log':
        log_file = selected_file
        log_file_label.config(text=log_file)
    elif file_type == 'data':
        data_file = selected_file
        data_file_label.config(text=data_file)
    elif file_type == 'replace':
        replace_file = selected_file
        replace_file_label.config(text=replace_file)

# Create main window
root = tk.Tk()
root.title("Data Processing App")

# Expand window dynamically based on content
root.geometry("600x500")
root.minsize(600, 500)  # Set minimum window size

# Center window on the screen
def center_window():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (600 // 2)
    y = (screen_height // 2) - (500 // 2)
    root.geometry(f"600x500+{x}+{y}")

center_window()

# Set grid weight to allow window resizing
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Main Menu Frame
main_menu_frame = tk.Frame(root)
main_menu_frame.grid(row=0, column=0, sticky="nsew")

tk.Label(main_menu_frame, text="Main Menu", font=("Helvetica", 20)).pack(pady=20)

create_output_button = tk.Button(main_menu_frame, text="Create Output", command=show_create_output_page)
create_output_button.pack(pady=10)

merge_outputs_button = tk.Button(main_menu_frame, text="Merge Outputs", command=show_merge_outputs_page)
merge_outputs_button.pack(pady=10)

# Create Output Frame
create_output_frame = tk.Frame(root)
create_output_frame.grid(row=0, column=0, sticky="nsew")

tk.Label(create_output_frame, text="Create Output Page", font=("Helvetica", 20)).pack(pady=20)

tk.Label(create_output_frame, text="Device ID:").pack()
device_id_entry = tk.Entry(create_output_frame)
device_id_entry.pack(pady=5)

tk.Label(create_output_frame, text="Log File:").pack()
log_file = ''
log_file_label = tk.Label(create_output_frame, text="No file selected")
log_file_label.pack(pady=5)
log_file_button = tk.Button(create_output_frame, text="Select Log File", command=lambda: select_file('log'))
log_file_button.pack(pady=5)

tk.Label(create_output_frame, text="Data File:").pack()
data_file = ''
data_file_label = tk.Label(create_output_frame, text="No file selected")
data_file_label.pack(pady=5)
data_file_button = tk.Button(create_output_frame, text="Select Data File", command=lambda: select_file('data'))
data_file_button.pack(pady=5)

# Add Replace File selection
tk.Label(create_output_frame, text="Replace File:").pack()
replace_file = ''
replace_file_label = tk.Label(create_output_frame, text="No file selected")
replace_file_label.pack(pady=5)
replace_file_button = tk.Button(create_output_frame, text="Select Replace File", command=lambda: select_file('replace'))
replace_file_button.pack(pady=5)

button_frame = tk.Frame(create_output_frame)
button_frame.pack(pady=20)

process_button = tk.Button(button_frame, text="Process Data", command=process_data, font=("Helvetica", 12, "bold"))
process_button.grid(row=0, column=0, padx=10)

back_to_main_menu_button1 = tk.Button(button_frame, text="Back to Main Menu", command=show_main_menu_page, font=("Helvetica", 12, "bold"))
back_to_main_menu_button1.grid(row=0, column=1, padx=10)

# Merge Outputs Frame
merge_outputs_frame = tk.Frame(root)
merge_outputs_frame.grid(row=0, column=0, sticky="nsew")

tk.Label(merge_outputs_frame, text="Merge Outputs Page", font=("Helvetica", 20)).pack(pady=20)

upload_button = tk.Button(merge_outputs_frame, text="Upload CSV Files", command=merge_files)
upload_button.pack(pady=10)

back_to_main_menu_button2 = tk.Button(merge_outputs_frame, text="Back to Main Menu", command=show_main_menu_page, font=("Helvetica", 12, "bold"))
back_to_main_menu_button2.pack(pady=10)

# Raise the main menu on startup
main_menu_frame.tkraise()

root.mainloop()
