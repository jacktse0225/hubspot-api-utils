import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
import sys
from datetime import datetime
import json

def save_directory():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'general', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    directory = config.get("selected_directory")
    return directory

##Read
def getting_file_name(file_paths):
    if isinstance(file_paths, tuple):
        if len(file_paths) > 1:
            now = datetime.now()
            file_name = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"
        else:
            file_name = os.path.basename(file_paths[0])
    else:
        file_name = os.path.basename(file_paths)
    file_name = file_name.split(".",1)[0]
    return file_name

def getting_file_path(directory, title, multiple=False, file_type=None):
    root = tk.Tk()
    root.withdraw()
    file_type_dict = {"csv":(("CSV files", "*.csv"), ("All files", "*.*")), "any":"", "xlsx":(("XLSX files", "*.xlsx"), ("All files", "*.*"))}
    if multiple:
        file_path = filedialog.askopenfilenames(
            initialdir=directory,
            title=title,
            filetypes=file_type_dict.get(file_type),
            multiple=True
        )
    else:
        file_path = filedialog.askopenfilename(
            initialdir=directory,
            title=title,
            filetypes=file_type_dict.get(file_type),
            multiple=False
        )
    if not file_path:
        print("No files selected.")
        return sys.exit()
    return file_path

def files_to_df(file_paths, file_type=None):
    data_frames = []
    if (file_type != "csv") and (file_type != "xlsx"):
        print("Selected file type is not supported.")
        sys.exit()
        return
    if file_type == "csv":
        for file_path in file_paths:
            df_add = pd.read_csv(file_path, encoding='utf-8')
            data_frames.append(df_add)
    if file_type == "xlsx":
        for file_path in file_paths:
            df_add = pd.read_excel(file_path)
            data_frames.append(df_add)
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df

def get_df_from_a_sheet_of_excel_file(save_directory, file_name, sheet_name):
    save_file = os.path.join(save_directory, f"{file_name}.xlsx")
    df = pd.read_excel(save_file, sheet_name=sheet_name)
    return df

def check_file_path(save_directory, file_name, file_type):
    save_file = os.path.join(save_directory, f"{file_name}.{file_type}")
    return os.path.isfile(save_file)

##Write

def create_excel_writer(file_name, backup, save_directory):
    save_file = os.path.join(save_directory, f"{file_name}.xlsx")
    if backup:
        now = datetime.now()
        save_file = os.path.join(save_directory, f"{file_name}-{now.hour}-{now.minute}-{now.second}.xlsx")
    writer = pd.ExcelWriter(save_file, engine='xlsxwriter')
    return writer



def excel_write_and_save(writer, df, sheet_name):
    df.to_excel(writer, sheet_name=f'{sheet_name}', index=False)
    sheet = writer.sheets[f'{sheet_name}']
    try:
        sheet.autofit()
    except:
        print(f"{sheet_name} Autofit Failed")



