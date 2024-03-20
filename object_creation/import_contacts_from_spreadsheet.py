import json
import sys
import numpy as np
import pandas as pd
from hubspot_api_utils.general.hubspot_api_functions import search_object, init_platform_api_directory, create_batch_of_objects, return_status_code
from hubspot_api_utils.general.readwrite import getting_file_path, files_to_df
import re
##Adjust the following list to meet your source of data
text_columns = ["Company Name", "First Name", "Last Name", "Job Title", "city", "state", "country"]



def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, email) is not None
def check_text_columns(df):
    for column in text_columns:
        # Check for unexpected or invalid values
        invalid_values = df[~df[column].str.isalnum()]
        if not invalid_values.empty:
            print(f"Warning: Invalid values found in {column}: {invalid_values}")
            sys.exit()

def data_cleaning(df, column_rename):
    df.drop_duplicates(subset=["email"], inplace=True)
    df.dropna(subset=["email"], inplace=True)
    df.drop(['Location'], axis=1, inplace=True)
    invalid_emails_index = df[df['email'].apply(lambda x: not validate_email(x))].index
    df.drop(invalid_emails_index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    ##Rename the Columns
    df.rename(columns=column_rename, inplace=True)
    return df

def fetch_company_id_by_domain(company_domains, headers, platform):
    for index, row in company_domains.iterrows():
        filtergroups = [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": row["URL"]}]}]
        result = search_object("company", filtergroups, ["num_associated_contacts"], headers, platform)
        company_id = np.nan
        if result:
            company_dict = {}
            for property in result:
                num_associated_contacts = property.get("num_associated_contacts")
                company_id = property.get("hs_object_id")
                company_dict.update({company_id: num_associated_contacts})
            company_id = max(company_dict, key=company_dict.get)
        company_domains.loc[index, "associatedcompanyid"] = company_id
    return company_domains

def create_property_for_parameter(df):
    payload = []
    for index, row in df.iterrows():
        row_dict = []
        for column in df.columns:
            if not pd.isna(row[column]) and column != "email":
                property = column
                value = row[column]
                row_dict.append({"property":property, "value":value})
        contact_dict = {"email": row["email"], "properties":row_dict}
        payload.append(contact_dict)
    return payload



def main():
    platform, api, directory, headers = init_platform_api_directory()
    file_type = input("xlsx or csv: ")
    ##Input Files
    file_path = getting_file_path(directory, True, file_type)
    df = files_to_df(file_path, file_type)

    ##Data Cleaning
    column_rename = {
        'Company Name': 'company',
        'First Name': 'firstname',
        'Last Name': 'lastname',
        'Linkedin URL': 'linkedin_url__c',
        'Phone Number': 'phone',
        'Job Title': 'jobtitle'
    }
    df = data_cleaning(df, column_rename)

    ##Find Company ID by domain
    company_domains = df[["URL"]].drop_duplicates()
    company_domains = fetch_company_id_by_domain(company_domains, headers, platform)
    df = df.merge(company_domains, on="URL", how="left")
    df.drop(["URL"], axis=1, inplace=True)
    ##Convert df to dict for the property in parameter
    properties = json.dumps(create_property_for_parameter(df))
    result = create_batch_of_objects("contact", properties, platform, headers)
    return_status_code(result)

if __name__ == "__main__":
    main()