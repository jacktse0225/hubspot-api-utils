import sys
import pandas as pd
from hubspot_api_utils.general import hubspot_api_functions, readwrite
import os
from datetime import datetime

"""
    This script is to associate Contact to Company by determining the contact's email domain and link it to the company by company domain
    If a Contact is available to associate, a system message will pop up. Users can view the contact and the company to be associated
    Press Enter to confirm the association or Input N to stop association
    A report will be generated as an Excel spreadsheet to show all Contacts associated and not associated
"""
def main():
    ##Input
    platform = input("sandbox or production: ")
    if platform == "":
        platform = "production"
    api, save_directory = hubspot_api_functions.reading_json_getting_api_and_save_directory(platform)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"Bearer {api}"
    }
    contact_associated = []
    contact_not_associated = []
    now = datetime.now()
    email_provider_domains_path = os.path.join(os.path.dirname(__file__), '..', 'lib', 'email_provider_domains.xlsx')
    try:
        with open(email_provider_domains_path):
            pass
    except FileNotFoundError:
        print("email_provider_domains.xlsx does not exist.")
        sys.exit()
    df = pd.read_excel(email_provider_domains_path)
    email_provider_domains = [item for sublist in df.values for item in sublist]
    ##Process
    filter_groups = [{"filters": [{"propertyName": "associatedcompanyid", "operator": "NOT_HAS_PROPERTY"}]}]
    result = hubspot_api_functions.search_object("contact", filter_groups, [], headers, platform)
    contact_list = [{"hs_object_id": item.get("id"), "email": item.get("email")} for item in result]
    for dict in contact_list:
        email = dict.get("email")
        id = dict.get("hs_object_id")
        if email:
            company_domain = email.split("@", 2)[-1]
            if company_domain not in email_provider_domains:
                filter_groups_company_domain = [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": company_domain}]}]
                print(f"Searching {id}'s Company by email")
                company_result = hubspot_api_functions.search_object("company", filter_groups_company_domain, ["num_associated_contacts"], headers, platform)
                company_dict = {}
                if company_result:
                    for property in company_result:
                        num_associated_contacts = property.get("num_associated_contacts")
                        company_id = property.get("hs_object_id")
                        company_dict.update({company_id: num_associated_contacts})
                    company_id_to_asso = max(company_dict, key=company_dict.get)
                    instruction = input(f"Press Enter to associate Contact: https://app.hubspot.com/contacts/{hubspot_api_functions.hs_platform_url.get(platform)}/record/0-1/{id} with Company https://app.hubspot.com/contacts/{hubspot_api_functions.hs_platform_url.get(platform)}/record/0-2/{company_id_to_asso} or input N to stop association. ")
                    if instruction == "":
                        hubspot_api_functions.associate_objects("contact", id, "company", company_id_to_asso, headers, platform)
                        print(f"Contact:{email} is associated to Company{company_domain}")
                        contact_associated.append([{"contact_id": int(id), "email": email, "company_domain": company_domain,"company_id": int(company_id_to_asso), "date": f"{now.year}-{now.month}-{now.day}"}])
                    else:
                        print(f"The association of Contact:{email} is stopped.")
                        contact_not_associated.append([{"contact_id": int(id), "email": email, "reason":"rejected","company_domain": company_domain,"company_id": int(company_id_to_asso)}])
                else:
                    print(f"{id}'s Company cannot be found by email")
                    contact_not_associated.append([{"contact_id": int(id), "email": email, "reason":"Companies cannot be found by email domain"}])
            else:
                print(f"{id}'s email domain is a email provider domain")
                contact_not_associated.append([{"contact_id": int(id), "email": email, "reason": "email provider domain"}])
        else:
            print(f"{id} does not have any email")
            contact_not_associated.append([{"contact_id": int(id), "reason":"no email"}])
    ##Write
    contact_associated = [item for sublist in contact_associated for item in sublist]
    contact_not_associated = [item for sublist in contact_not_associated for item in sublist]
    contact_wout_companies_df = pd.DataFrame(contact_list)
    contact_associated_df = pd.DataFrame(contact_associated)
    contact_not_associated_df = pd.DataFrame(contact_not_associated)
    file_name = f"contacts_associated_company-{platform}"
    file_path = os.path.join(save_directory, f"{file_name}.xlsx")
    try:
        with open(file_path):
            contact_associated_df_ori = readwrite.get_df_from_a_sheet_of_excel_file(save_directory, file_name, sheet_name="contact_associated")
            if not contact_associated_df_ori.empty and not contact_associated_df.empty:
                contact_associated_df = pd.concat([contact_associated_df_ori, contact_associated_df])
            elif not contact_associated_df_ori.empty and contact_associated_df.empty:
                contact_associated_df = contact_associated_df_ori
    except FileNotFoundError:
        print("Creating new Excel file")
    ##Save
    writer = readwrite.create_excel_writer(f"contacts_associated_company-{platform}", False,save_directory)
    readwrite.excel_write_and_save(writer, contact_wout_companies_df, "contact_wout_company")
    readwrite.excel_write_and_save(writer, contact_associated_df, "contact_associated")
    readwrite.excel_write_and_save(writer, contact_not_associated_df, "contact_not_associated")
    writer.close()

if __name__ == "__main__":
    main()
