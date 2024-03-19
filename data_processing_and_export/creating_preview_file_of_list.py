import pandas as pd
import hubspot
import sys
from hubspot_api_utils.general import hubspot_api_functions, readwrite

def title_analysis_formatting(contact_list, company_list, industry_label):
    df = pd.DataFrame(contact_list)
    df = df.rename(columns = {"associatedcompanyid" : "company_id", "jobtitle":"job_title", "job_function":"job_function",
                              "management_level_l__c":"management_level", "hs_object_id":"contact_id","city":"contact_city", "country":"contact_country", "state":"contact_state"})
    if company_list:
        company_df = pd.DataFrame(company_list)
        company_df = company_df.merge(industry_label, left_on="industry", right_on="value", how="left").drop(["industry", "value"], axis=1)
        company_df = company_df.rename(columns={"city":"company_city", "country":"company_country", "annualrevenue":"annual_revenue", "hs_object_id":"company_id", "name":"company_name",
                                                "numberofemployees":"number_of_employees", "label":"company_industry"})
        df = df.merge(company_df, how="left", on="company_id")
        title_analysis = df[
            ["company_name", "job_title", "management_level", "job_function", "company_industry", "contact_city", "contact_state",
             "contact_country","annual_revenue", "contact_id"]]
    else:
        title_analysis = df[["company", "job_title", "management_level", "job_function", "industry", "contact_city","contact_state","contact_country", "contact_id"]]
    title_analysis = title_analysis.drop_duplicates()
    return title_analysis

def company_analysis_formatting(company_list, industry_label):
    if company_list:
        company_df = pd.DataFrame(company_list)
        company_df = company_df.merge(industry_label, left_on="industry", right_on="value", how="left").drop(["industry", "value"], axis=1)
        company_df = company_df.rename(
                columns={"city": "company_city", "state": "company_state", "country": "company_country", "annualrevenue": "annual_revenue",
                         "hs_object_id": "company_id", "name": "company_name",
                         "numberofemployees": "number_of_employees", "label":"industry"})
        company_analysis = company_df[
                ["company_name", "industry", "annual_revenue", "number_of_employees", "company_city", "company_state","company_country",
                 "company_id"]]
        company_analysis = company_analysis.drop_duplicates()
    else:
        company_analysis = pd.DataFrame(company_list)
    return company_analysis

def main():
    ##Input
    platform = input("sandbox or production: ")
    if platform == "":
        platform = "production"
    list_name = input("List Name: ")
    api, save_directory = hubspot_api_functions.reading_json_getting_api_and_save_directory(platform)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"Bearer {api}"
    }
    client = hubspot.Client.create(access_token=api)
    contact_properties = ["city", "country", "management_level_l__c", "job_function", "jobtitle", "associatedcompanyid",
                             "state", "company", "industry"]
    company_properties = ["name", "city", "state","country", "industry", "annualrevenue", "numberofemployees"]

    ##Process
    list_info = hubspot_api_functions.search_list_with_list_name(list_name, headers)
    if not list_info:
        print("list is not found. Please check the list name.")
        sys.exit()
    ils_id = list_info[0].get("listId")
    list_size = int(list_info[0].get("hs_list_size"))
    if list_size == 0:
        print("The list is empty")
        sys.exit()
    contact_id = hubspot_api_functions.fetch_contact_ids_from_a_list(ils_id, headers, list_size)
    contact_id = hubspot_api_functions.convert_ids_to_v4_format(contact_id)
    contact_list = hubspot_api_functions.get_contact_info_as_list(contact_id, client, contact_properties)
    company_list_ids = hubspot_api_functions.get_company_ids_from_contact_list(contact_list)
    company_list = hubspot_api_functions.get_company_info_as_list(company_list_ids, client, company_properties)
    industry_label = hubspot_api_functions.get_label_value_of_property(headers, "companies", "industry")

    ##Formatting
    title_analysis = title_analysis_formatting(contact_list, company_list, industry_label)
    company_analysis = company_analysis_formatting(company_list, industry_label)
    writer = readwrite.create_excel_writer(list_name, False, save_directory)
    readwrite.excel_write_and_save(writer, title_analysis, "title_analysis")
    readwrite.excel_write_and_save(writer, company_analysis, "company_analysis")
    writer.close()


if __name__ == "__main__":
    main()