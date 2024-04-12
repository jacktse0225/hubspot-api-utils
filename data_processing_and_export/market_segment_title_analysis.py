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
    comp_file = getting_file_path(current_directory, 'Select Comp csv',False, 'csv')

    conference_name = input('Input conference short name: ')
    writer = create_excel_writer(f"{conference_name} GP - Market Segment & Title Analysis - 2024.xlsx", False, download_directory)
    current_year = datetime.now().year
    year_column = [str(year) for year in range(current_year, 2007, -1)]

    ori_paid_company = pd.read_csv(company_file, encoding='utf-8')
    ori_paid_title = pd.read_csv(title_file, encoding='utf-8')
    comp_df = pd.read_csv(comp_file, encoding='utf-8')

    ##Formatting
    paid_company = paid_company_formatting(writer, ori_paid_company, year_column)
    paid_title = paid_title_formatting(writer, ori_paid_title, year_column)
    comp_company = comp_company_formatting(writer, comp_df, year_column)
    comp_title = comp_title_formatting(writer, comp_df, year_column)
    company_per_event = company_per_event_formatting(writer, paid_company, comp_company, year_column)
    attendee_per_event = attendee_per_event_formatting(writer, paid_title, comp_title, year_column)
    company_compilation = company_compilation_formatting(writer, ori_paid_company, comp_df)
    attendee_compilation = attendee_compilation_formatting(writer, ori_paid_title, comp_df)
    title_analysis = title_analysis_formatting(writer, attendee_compilation)
    writer.close()

if __name__ == "__main__":
    main()