import requests
import time
import pandas as pd
import numpy as np
import json
import sys
import hubspot
from hubspot.crm.contacts import BatchReadInputSimplePublicObjectId, ApiException
from hubspot.crm.companies import BatchInputSimplePublicObjectInputForCreate, ApiException
from pprint import pprint
import os

hs_objecttype_and_obejctid = {"production":{"contact":"contact","company":"companies", "conference_role":"2-5487873", "conference":"2-5436849",
                              "deal":"deal", "list":"list"}, "sandbox":{"contact":"contact","company":"companies",
                              "deal":"deal", "list":"list", "conference_role":"2-9428547", "conference":"2-9428549"}}

object_typeid = {"production":{"contact":"0-1","company":"0-2", "conference_role":"2-5487873", "conference":"2-5436849",
                              "deal":"0-3"}, "sandbox":{"contact":"0-1","company":"0-2",
                              "deal":"0-3", "conference_role":"2-9428547", "conference":"2-9428549"}}


object_type_for_properties = {"production":{"contact":"contacts","company":"companies", "conference_role":"2-5487873", "conference":"2-5436849",
                              "deal":"deals", "list":"lists"}, "sandbox":{"contact":"contacts","company":"companies",
                              "deal":"deals", "list":"lists", "conference_role":"2-9428547", "conference":"2-9428549"}}

hs_platform_url = {"production":"21235114", "sandbox":"23157964"}

##Input
def reading_json_getting_api_and_save_directory(platform):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'general', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    save_directory = config.get("selected_directory")
    if platform == "sandbox":
        api = config.get("sandbox_api")
    elif platform == "production":
        api = config.get("production_api")
    else:
        print("Please choose between sandbox or production")
        sys.exit()
    return api, save_directory

##Limit Remaining
def api_limit_remaining(headers):
    url = "https://api.hubapi.com/properties/v1/contacts/properties"
    response = requests.get(url, headers=headers)
    remaining_daily_limit = response.headers.get('X-HubSpot-RateLimit-Daily-Remaining')
    print(remaining_daily_limit)
    return remaining_daily_limit

##Object Properties
def get_object_all_properties(object, headers, platform):
    if object not in object_type_for_properties.get(platform):
        print(f"{object} is not found")
        return sys.exit()
    object_type = object_type_for_properties.get(platform).get(object)
    url = f"https://api.hubapi.com/properties/v1/{object_type}/properties"
    response = requests.get(url, headers=headers).json()
    print(response)
    return response

def search_object(object, filter_groups, properties, headers, platform):
    if object not in object_type_for_properties.get(platform):
        print(f"{object} is not found")
        return sys.exit()
    object_type = object_type_for_properties.get(platform).get(object)
    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/search"
    payload = {"limit": "100", "after": "0", "filterGroups": filter_groups, "properties": properties}
    result_list = []
    after_value = 0
    batch_size = 100
    time_sleep = 1
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 400:
        print(response.json())
        print("Filters are incorrect. Please adjust the filters.")
        sys.exit()
    elif response.status_code != 200:
        print(f"Error:{response.status_code}. Sleep {time_sleep} seconds")
        time.sleep(time_sleep)
        response = requests.post(url, headers=headers, json=payload)

    total_size = response.json().get("total")
    total_batch = np.ceil(total_size / batch_size).astype(int)
    for batch in range(total_batch):
        print("Searching object")
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error:{response.status_code}. Sleep {time_sleep} seconds")
            time.sleep(time_sleep)
            response = requests.post(url, headers=headers, json=payload)
        result = response.json().get("results")
        if result is not None:
            result_list.append(result)
        after_value += 100
        payload["after"] = after_value
        progress = round(after_value / total_size * 100)
        if progress > 100:
            progress = 100
        print(f"Progress: {progress}%")
    if not result_list:
        result_list = []
    result = [item for sublist in result_list for item in sublist if item is not None]

    for dict in result:
        property = dict.get("properties")
        for key, value in property.items():
            dict.update({key: value})
    return result

def get_object_id_from_object_type_to_object_type(object_from, object_to, objectId, headers, platform):
    objectType = hs_objecttype_and_obejctid.get(platform).get(object_from)
    toObjectType = hs_objecttype_and_obejctid.get(platform).get(object_to)
    url = f"https://api.hubapi.com/crm/v4/objects/{objectType}/{objectId}/associations/{toObjectType}"
    result = requests.get(url, headers=headers).json().get("results")
    id = []
    if not result:
        print(f"{object_to}: Object ID is not found")
        return id
    if len(result) > 1:
        for item in result:
            id.append(item.get("toObjectId"))
            print(f"{object_to}: Object IDs are found")
        return id
    id_output = result[0].get("toObjectId")
    print(f"{object_to}: {id_output}")
    return id_output

def associate_objects(object_type_from, object_id_from, object_type_to, object_id_to, headers, platform):
    objectTypeFrom = hs_objecttype_and_obejctid.get(platform).get(object_type_from)
    objectTypeTo = hs_objecttype_and_obejctid.get(platform).get(object_type_to)
    url = f"https://api.hubapi.com/crm/v4/objects/{objectTypeFrom}/{object_id_from}/associations/default/{objectTypeTo}/{object_id_to}"
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        print(f"{object_type_from}:{object_id_from} is associated to {object_type_to}:{object_id_to}")
    else:
        print(f"{object_type_from}:{object_id_from} to {object_type_to}:{object_id_to} is FAILED.")
    return


def update_properties_in_object(object_type, object_id, properties, headers, platform):
    objectType = object_type_for_properties.get(platform).get(object_type)
    payload = {"properties": properties}
    url = f"https://api.hubspot.com/crm/v3/objects/{objectType}/{object_id}"
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Properties of {object_type}:{object_id} are updated")
    else:
        print(f"Failed to update properties of {object_type}:{object_id}.")
        print(response.json())
    return

def get_property_values_from_object(objectType, property_name, headers, platform):
    objectType = object_type_for_properties.get(platform).get(objectType)
    url = f"https://api.hubspot.com/crm/v3/properties/{objectType}/{property_name}"
    result = requests.get(url, headers=headers).json()
    return result

def get_label_value_of_property(headers, objectType, property_name):
    url = f"https://api.hubspot.com/crm/v3/properties/{objectType}/{property_name}"
    result = requests.get(url, headers=headers).json()
    if not result["options"]:
        result["options"] = []
    list = []
    for option in result["options"]:
        label = option["label"]
        value = option["value"]
        list.append({"label": label, "value": value})
    df = pd.DataFrame(list)
    return df

def conference_roles_wout_asso_company(platform, headers):
    cr_id = hs_objecttype_and_obejctid.get(platform).get("conference_role")
    if not cr_id:
        print("Input is incorrect. Please choose betweem conference_role_sandbox or conference_role_production")
        sys.exit()
    ## add if
    url = f"https://api.hubspot.com/crm/v3/objects/{cr_id}?associations=company&limit=100"
    cr_without_company_list = []
    batch = 0
    while url:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        result = response_json.get("results")
        print(f"Fetching CR with Associated Company: Batch {batch}")
        for n in result:
            association = n.get("associations", None)
            if association is None:
                id = n.get("id")
                cr_without_company_list.append(id)
        paging = response_json.get("paging", None)
        if paging is not None:
            next_link = paging.get("next", {}).get("link")
            batch += 1
            url = next_link
            time.sleep(10)
        else:
            break
    return cr_without_company_list

##Lists


def fetch_list_with_list_name(object_type, list_name, platform, headers):
    object_type_id = object_typeid.get(platform).get(object_type)
    url = f"https://api.hubapi.com/crm/v3/lists/object-type-id/{object_type_id}/name/{list_name}"
    querystring = {"includeFilters": "true"}
    result = requests.get(url, headers=headers, params=querystring).json()
    return result


##contact list only
def search_list_with_list_name(list_name, headers):
    url = "https://api.hubapi.com/crm/v3/lists/search"
    offset = 0
    count = 500
    data = []
    counter = 0
    if not list_name:
        list_name = ""
    payload = {"count": count, "offset": offset, "query": list_name}
    result = requests.post(url, json=payload, headers=headers).json()
    total_size = result.get("total")
    total_batch = np.ceil(total_size / count).astype(int)
    for batch in range(total_batch):
        payload = {"count": count, "offset": offset, "query": list_name}
        response = requests.post(url, json=payload, headers=headers)
        counter += 1
        result = response.json()
        data.append(result.get("lists"))
        print(f"V3 Search List{counter}")
        offset = result.get("offset")
    list = [item for sublist in data for item in sublist]
    for dict in list:
        property = dict.get("additionalProperties")
        for key, value in property.items():
            dict.update({key: value})
    return list

def get_all_lists_v1(headers):
    list_url = "https://api.hubapi.com/contacts/v1/lists?count=100"
    offset = 0
    list_info_in_list = []
    counter = 1

    while True:
        print(f"Preparing V1 hs_list_data: {counter}")
        list_response = requests.get(f"{list_url}&offset={offset}", headers=headers)
        list_response_json = list_response.json()
        list_info = list_response_json.get("lists")
        list_info_in_list.append(list_info)
        if not list_response_json["has-more"]:
            break
        offset = list_response_json["offset"]
        counter += 1
    list_info = [item for sublist in list_info_in_list for item in sublist]
    for dict in list_info:
        property = dict.get("metaData")
        for key, value in property.items():
            dict.update({key: value})
    return list_info

def fetch_contact_ids_from_a_list(internal_id, headers, list_size):
    url = f"https://api.hubapi.com/crm/v3/lists/{internal_id}/memberships"
    limit = 250
    querystring = {"limit":limit}
    contact_id = []
    counter = 1
    total_batch = np.ceil(list_size / limit).astype(int)
    for batch in range(total_batch):
        response = requests.get(url=url, headers=headers, params=querystring)
        if response.status_code != 200:
            return []
        response = response.json()
        contact_id.append(response.get("results"))
        if batch < (total_batch-1):
            new_url = response.get("paging").get("next").get("link")
            url = new_url
        print(f"Fetching Contact IDs: Batch {counter}")
        counter += 1
    contact_id = [item for sublist in contact_id for item in sublist]
    return contact_id

def convert_ids_to_v4_format(list):
    contact_ids = [{"id": id["recordId"]} for id in list]
    return contact_ids


def get_all_contact_ids_from_a_list(list_id, headers, size):
    count_per_batch = 100
    url = f"https://api.hubapi.com/contacts/v1/lists/{list_id}/contacts/all?count={count_per_batch}"
    all_contact_ids = []
    offset = 0
    total_batch = np.ceil(size/count_per_batch).astype(int)
    for batch in range(total_batch):
        response = requests.get(f"{url}&vidOffset={offset}", headers=headers)
        data = response.json()
        print(data)
        contact_ids = [contact["vid"] for contact in data["contacts"]]
        all_contact_ids.append(contact_ids)
        process = count_per_batch*(batch+1)/size*100
        if process > 100:
            process = 100
        print(f"Getting All Contact IDs from HS: {round(process)}%")
        offset = data["vid-offset"]
    print("Getting All Contact IDs from HS: Done")
    all_contact_ids = [item for sublist in all_contact_ids for item in sublist]
    return all_contact_ids



##Contact
def get_contact_info_as_list(all_contact_ids, client, contact_properties):
    max_batch_size = 100
    contact_batches = [all_contact_ids[i:i + max_batch_size] for i in range(0, len(all_contact_ids), max_batch_size)]
    contact_results = []
    contact = []
    datafeteched = 0
    for batch_contact_ids in contact_batches:
        batch_read_input_simple_public_object_id = BatchReadInputSimplePublicObjectId(
            properties= contact_properties,
            inputs=batch_contact_ids)
        try:
            batch_contact_response = client.crm.contacts.batch_api.read(
                batch_read_input_simple_public_object_id=batch_read_input_simple_public_object_id, archived=False)
            contact_results.append(batch_contact_response.results)
            max_data = len(all_contact_ids)
            progress_percentage = (datafeteched / max_data) * 100
            if progress_percentage > 100:
                progress_percentage = 100
            print(f"Getting Contact Info From HS: {round(progress_percentage)}%")
            datafeteched += max_batch_size
        except ApiException as e:
            print("Exception when calling batch_api->read: %s\n" % e)
    contact_list = [item for sublist in contact_results for item in sublist]
    for dict in contact_list:
        contact.append(dict.properties)
    return contact

def get_contact_list_membership(contact_ids, headers, list_data_df):
    base_url = "https://api.hubapi.com/contacts/v1/contact/vids/batch/"
    batch_size = 100
    total_contacts = len(contact_ids)
    response_list = []
    standard_list_membership = []
    datafeteched = 0
    for start_idx in range(0, total_contacts, batch_size):
        batch_contact_ids = contact_ids[start_idx:start_idx + batch_size]
        vid_params = "&".join([f"vid={contact_id}" for contact_id in batch_contact_ids])
        final_url = f"{base_url}?{vid_params}&showListMemberships=true"

        response = requests.get(final_url, headers=headers)
        response_json = response.json()
        for contact_id in batch_contact_ids:
            contact_info = response_json.get(str(contact_id), {})
            list_memberships = contact_info.get("list-memberships", [])
            combined_properties = {"Contact ID": contact_id}

            for membership in list_memberships:
                list_id = membership.get("static-list-id")
                if list_id in list_data_df["listId"].to_list():
                    name = list_data_df.loc[list_data_df['listId'] == list_id, 'name'].values[0]
                    combined_properties[f"{name}"] = 1
                    if name not in standard_list_membership:
                        standard_list_membership.append(name)

            response_list.append(combined_properties)

        progress_percentage = (datafeteched / total_contacts) * 100
        print(f"Getting Contact List Membership From HS: {round(progress_percentage)}%")
        datafeteched += batch_size
    df = pd.DataFrame(response_list)
    return df, standard_list_membership

##Contact and Company
def get_company_ids_from_contact_list(contact_list):
    company_list = []
    for dict in contact_list:
        if dict.get("associatedcompanyid") and dict.get("associatedcompanyid") not in company_list:
            company_list.append(dict.get("associatedcompanyid"))
    return company_list

def concat_contact_and_company_info(contact_df, company_df):
    df = pd.merge(contact_df, company_df, how='left', left_on="contact_associatedcompanyid", right_on="company_hs_object_id")
    df.columns = [x.lower().replace(' ', '_') for x in df.columns]
    return df

##Company
def get_company_info_as_list(company_id_list, client, company_properties):
    max_batch_size = 100
    company_batches = [company_id_list[i:i + max_batch_size] for i in range(0, len(company_id_list), max_batch_size)]
    datafeteched = 0
    max_data = len(company_id_list)
    company_results = []
    for batch_company_ids in company_batches:
        batch_read_input_simple_public_object_id = BatchReadInputSimplePublicObjectId(properties= company_properties,
                                                                                      inputs=batch_company_ids)
        try:
            batch_company_response = client.crm.companies.batch_api.read(
                batch_read_input_simple_public_object_id=batch_read_input_simple_public_object_id, archived=False)
            company_results.append(batch_company_response.results)
            progress_percentage = (datafeteched / max_data) * 100
            print(f"Getting Company Info From HS: {round(progress_percentage)}%")
            datafeteched += max_batch_size
        except ApiException as e:
            print("Exception when calling batch_api->read: %s\n" % e)
    company = []
    company_list = [item for sublist in company_results for item in sublist]
    for dict in company_list:
        company.append(dict.properties)
    return company

def init_platform_api_directory():
    platform = input("sandbox or production: ")
    if platform == "":
        platform = "production"
    api, directory = reading_json_getting_api_and_save_directory(platform)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"Bearer {api}"
    }
    client = hubspot.Client.create(access_token=api)
    return platform, api, directory, headers, client

def create_batch_of_companies(client, parameters):
    result = []
    batches = []
    for i in range(0, len(parameters), 100):
        batch = parameters[i:i + 100]
        batches.append(batch)
    for batch in batches:
        batch_input_simple_public_object_input_for_create = BatchInputSimplePublicObjectInputForCreate(inputs=batch)
        api_response = client.crm.companies.batch_api.create(batch_input_simple_public_object_input_for_create=batch_input_simple_public_object_input_for_create)
        result.append(api_response.to_dict())
    return result

def create_batch_of_contacts(client, parameters):
    result = []
    batches = []
    for i in range(0, len(parameters), 100):
        batch = parameters[i:i + 100]
        batches.append(batch)
    for batch in batches:
        batch_input_simple_public_object_input_for_create = BatchInputSimplePublicObjectInputForCreate(inputs=batch)
        api_response = client.crm.contacts.batch_api.create(batch_input_simple_public_object_input_for_create=batch_input_simple_public_object_input_for_create)
        result.append(api_response.to_dict())
    return result

def return_status_code(status_code):
    if status_code in [200,202]:
        print("Data is successfully imported!")
    else:
        print("Data Import is failed")

# def mapping_industry_label_to_value(industry):
def get_property_values_from_object_v3(client, platform, object_type, property_name):
    if object_type not in object_type_for_properties.get(platform):
        print(f"{object_type} is not found")
        return sys.exit()
    object_type = object_type_for_properties.get(platform).get(object_type)
    api_response = client.crm.properties.core_api.get_by_name(object_type=object_type, property_name=property_name, archived=False).to_dict()
    return api_response