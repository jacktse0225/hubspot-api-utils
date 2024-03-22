import sys
import numpy as np
import pandas as pd
from hubspot_api_utils.general.hubspot_api_functions import search_object, init_platform_api_directory, create_batch_of_companies, return_status_code, get_property_values_from_object_v3, create_batch_of_contacts
from hubspot_api_utils.general.readwrite import getting_file_path, files_to_df, create_excel_writer, excel_write_and_save
import re


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, email) is not None

def website_to_domain(website):
    to_remove = 'http://www.'
    if website:
        domain = website.replace(to_remove, '')
    else:
        domain = np.nan
    return domain

def data_cleaning(df):
    df.drop_duplicates(subset=["Email"], inplace=True)
    df.dropna(subset=["Email"], inplace=True)
    invalid_emails_index = df[df['Email'].apply(lambda x: not validate_email(x))].index
    df.drop(invalid_emails_index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['Website'] = df['Website'].apply(lambda x: website_to_domain(x))
    return df

def fetch_company_id_by_domain(company_domains, headers, platform):
    for index, row in company_domains.iterrows():
        filtergroups = [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": row["Website"]}]}]
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

def create_object_df(df, columns_to_rename, object_columns):
    df = df[object_columns]
    df.rename(columns = columns_to_rename, inplace=True)
    return df
def create_property_for_parameter(df):
    payload = []
    for index, row in df.iterrows():
        row_dict = {}
        for column in df.columns:
            if not pd.isna(row[column]):
                property = column
                value = row[column]
                row_dict[property] = value
        payload.append({'properties': row_dict})
    return payload

def convert_industry_label_to_value(client, platform, df):
    industry_response = get_property_values_from_object_v3(client, platform, "company", "industry")
    options = industry_response['options']
    list = []
    for option in options:
        dict = {'industry': option['label'], 'industry_value': option['value']}
        list.append(dict)
    industry_df = pd.DataFrame(list)
    df = df.merge(industry_df, left_on="Industry", right_on='industry', how='left')
    return df

def creating_asso_company(client, df, contact_df, company_column_rename, company_df_columns):
    company_df = create_object_df(df, company_column_rename, company_df_columns)
    company_df = company_df[company_df['associatedcompanyid'].isna()]
    if not company_df['associatedcompanyid'].empty:
        company_df.drop(['associatedcompanyid'], axis=1, inplace=True)
        properties = create_property_for_parameter(company_df)
        company_result = create_batch_of_companies(client, properties)
        company_created = []
        for company in company_result:
            info = company['results'][0]
            associatedcompanyid = info['id']
            company_created.append({'associatedcompanyid': associatedcompanyid})
        company_created_df = pd.DataFrame(company_created)
        company_created_df['associatedcompanyid'] = company_created_df['associatedcompanyid'].astype(object)
    return company_created_df

def creating_list_for_contacts_imported(result):
    contacts_imported = []
    for new_contacts in result:
        id = new_contacts['results'][0]['id']
        email = new_contacts['results'][0]['properties']['email']
        contacts_imported.append({"contact_id": id, "email": email})
    return contacts_imported
def main():
    platform, api, directory, headers, client = init_platform_api_directory()

    file_type = input("xlsx or csv: ")
    ##Input Files
    file_path = getting_file_path(directory, True, file_type)
    df = files_to_df(file_path, file_type)
    contact_df_columns = ['Company', 'Email', 'First Name', 'Last Name', 'Person Linkedin Url', 'First Phone', 'Title', 'City', 'State', 'Country', 'industry_value', 'Website', 'associatedcompanyid']
    company_df_columns = ['Company', 'Corporate Phone', 'industry_value', '# Employees', 'Website', 'Company Linkedin Url', 'Facebook Url', 'Twitter Url', 'Company City', 'Company State', 'Company Country', 'Annual Revenue', 'associatedcompanyid']
    ##Data Cleaning
    contact_column_rename = {
        'Company': 'company',
        'First Name': 'firstname',
        'Last Name': 'lastname',
        'Person Linkedin Url': 'linkedin_url__c',
        'First Phone': 'phone',
        'Title': 'jobtitle',
        'City':'city',
        'State':'state',
        'Country':'country',
        '# Employees':'numemployees',
        'industry_value':'industry',
        'Email':'email'
    }

    company_column_rename ={
        'Company': 'name',
        'Website': 'domain',
        'Corporate Phone':'phone',
        'industry_value':'industry',
        '# Employees':'numberofemployees',
        'Company Linkedin Url':'linkedin_company_page',
        'Facebook Url':'facebook_company_page',
        'Twitter Url':'twitterbio',
        'Company City':'city',
        'Company State':'state',
        'Company Country':'country',
        'Annual Revenue':'annualrevenue'
    }

    df = data_cleaning(df)
    ##Find Company ID by domain
    company_domains = df[["Website"]].drop_duplicates()
    company_id = fetch_company_id_by_domain(company_domains, headers, platform)
    df = df.merge(company_id, on="Website", how="left")
    ##Convert Industry label to value
    df = convert_industry_label_to_value(client, platform, df)
    contact_df = create_object_df(df, contact_column_rename, contact_df_columns)
    ##Create Company if any
    company_created_df = creating_asso_company(client, df, contact_df, company_column_rename, company_df_columns)
    contact_df['associatedcompanyid'] = contact_df['associatedcompanyid'].astype(object)
    contact_df = contact_df.merge(company_created_df, on='associatedcompanyid', how='left')

    #Convert df to dict for the property in parameter
    contact_df.drop(["Website"], axis=1, inplace=True)
    properties = create_property_for_parameter(contact_df)
    result = create_batch_of_contacts(client, properties)
    contacts_imported = creating_list_for_contacts_imported(result)

    ##Write&Save
    writer = create_excel_writer("hs_contacts_imported", True, directory)
    df = pd.DataFrame(contacts_imported)
    excel_write_and_save(writer, df, "new_data_imported")
    writer.close()

if __name__ == "__main__":
    main()