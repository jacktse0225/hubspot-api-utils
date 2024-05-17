import pandas as pd
import os
from hubspot_api_utils.general.market_segment_title_analysis_function import paid_company_formatting, comp_company_formatting, company_per_event_formatting, paid_title_formatting, comp_title_formatting, company_compilation_formatting, attendee_per_event_formatting, attendee_compilation_formatting, title_analysis_formatting
from hubspot_api_utils.general.readwrite import getting_file_path, create_excel_writer, save_directory
from datetime import datetime

def main():
    download_directory = save_directory()
    current_directory = os.getcwd()
    company_file = getting_file_path(current_directory, 'Select Company csv',False, 'csv')
    title_file = getting_file_path(current_directory, 'Select Title csv',False, 'csv')
    conference_name = input('Input conference short name: ')

    writer = create_excel_writer(f"{conference_name} GS - Market Segment & Title Analysis - 2024.xlsx", False, download_directory)
    current_year = datetime.now().year
    year_column = [str(year) for year in range(current_year, 2007, -1)]
    title = paid_title_formatting(writer, title_file, year_column)
    company = paid_company_formatting(writer, company_file, year_column)

    writer.close()
if __name__ == "__main__":
    main()