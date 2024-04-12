import pandas as pd
from hubspot_api_utils.general.readwrite import getting_file_path, create_excel_writer, excel_write_and_save

def concat_values(series):
    return ', '.join(series)
def paid_company_formatting(writer, df, year_column):
    ##paid company
    df.columns = [x.lower() for x in df.columns]
    df.columns = [x.replace(' ', '_') for x in df.columns]
    df["annual_revenue"] = df["annual_revenue"].replace('(No value)', 0).astype(float).round(0)
    df["number_of_employees"] = df["number_of_employees"].replace('(No value)', 0).astype(float).round(0)
    df["year"] = '20' + df["conference_code"].astype(str).str[1:3]
    df["company_id"] = df["company_id"].astype(str)
    df["year_and_id"] = df["year"] + df["company_id"]

    df = df.groupby(["year_and_id"], as_index=False).agg(
            {"amount": "sum", "number_of_associated_contacts":"sum",**{col: "first" for col in df.columns if col not in ["amount", "year_and_id", "number_of_associated_contacts"]}}
        )

    all_columns = df.columns.tolist() + year_column
    df = df.reindex(columns=all_columns)

    for index, row in df.iterrows():
        year = row["year"]
        if year in year_column:
            df.at[index, year] = 1

    df = df.groupby(["company_id"], as_index=False).agg(
        {"amount": "sum", "number_of_associated_contacts":"sum", **{column: "sum" for column in year_column}, **{col: "first" for col in df.columns if col not in ["number_of_associated_contacts", "amount"]+year_column}}
    )
    df["count"] = df[year_column].sum(axis=1)
    final_columns = ["company_name", "industry", "city_company", "country/region_company", "annual_revenue", "number_of_employees", "company_id", "number_of_associated_contacts", "amount", "count"] + year_column
    df = df.reindex(columns=final_columns)
    df.rename(columns = {'number_of_associated_contacts':'no_of_attendees'}, inplace=True)
    for index, row in df.iterrows():
            for year in year_column:
                if df.at[index, year] == 0:
                    df.at[index, year] = ""
    df.columns = df.columns.str.replace("_", " ")
    df_columns = df.columns.to_list()
    df.columns = [x.capitalize() for x in df_columns]
    excel_write_and_save(writer, df, "Paid Company")
    return df

def paid_title_formatting(writer, df, year_column):
    df.columns = [x.lower() for x in df.columns]
    df.columns = [x.replace(' ', '_') for x in df.columns]
    df = df[df["contact_id"] != "(No value)"]
    df["amount"] = df["amount"] / df["number_of_associated_contacts"]
    df["year"] = '20' + df["conference_code"].astype(str).str[1:3]
    df["contact_id"] = df["contact_id"].astype(str)
    df["year_and_id"] = df["year"] + df["contact_id"]
    df = df.groupby(["year_and_id"], as_index=False).agg(
        {"amount": "sum", **{col: "first" for col in df.columns if col not in ["amount", "year_and_id"]}}
    )
    all_columns = df.columns.tolist() + year_column
    df = df.reindex(columns=all_columns)
    for index, row in df.iterrows():
        year = row["year"]
        if year in year_column:
            df.at[index, year] = 1

    df = df.groupby(["contact_id"], as_index=False).agg(
        {"amount": "sum", **{column: "sum" for column in year_column},
         **{col: "first" for col in df.columns if col not in ["amount"] + year_column}}
    )
    df["count"] = df[year_column].sum(axis=1)
    final_columns = ["company_name", "first_name", "last_name", "job_title", "city", "country/region",
                     "management_level", "contact_id", "amount", "count"] + year_column
    df = df.reindex(columns=final_columns)
    for index, row in df.iterrows():
        for year in year_column:
            if df.at[index, year] == 0:
                df.at[index, year] = ""
    df.columns = df.columns.str.replace("_", " ")
    df_columns = df.columns.to_list()
    df.columns = [x.capitalize() for x in df_columns]
    excel_write_and_save(writer, df, "Paid Contact")
    return df

def comp_company_formatting(writer, df, year_column):
    df.columns = [x.lower() for x in df.columns]
    df.columns = [x.replace(' ', '_') for x in df.columns]
    df["annual_revenue"] = df["annual_revenue"].replace('(No value)', 0).astype(float)
    df["number_of_employees"] = df["number_of_employees"].replace('(No value)', 0).astype(float)
    df_columns_to_drop = ["first_name", "last_name", "job_title", "city", "country/region", "management_level", "email",
                          "phone_number"]
    df = df.drop(df_columns_to_drop, axis=1)
    df["year"] = '20' + df["conference_code"].astype(str).str[1:3]
    df["company_id"] = df["company_id"].astype(str)
    df["year_and_id"] = df["year"] + df["company_id"]

    df = df.groupby(["year_and_id"], as_index=False).agg(
        {"contact_id": "count",
         **{col: "first" for col in df.columns if col not in ["year_and_id", "contact_id"]}}
    )
    df.rename(columns={'contact_id': 'number_of_associated_contacts'}, inplace=True)
    all_columns = df.columns.tolist() + year_column
    df = df.reindex(columns=all_columns)

    for index, row in df.iterrows():
        year = row["year"]
        if year in year_column:
            df.at[index, year] = 1

    df = df.groupby(["company_id"], as_index=False).agg(
        {"number_of_associated_contacts": "sum", **{column: "sum" for column in year_column},
         **{col: "first" for col in df.columns if col not in ["number_of_associated_contacts", "amount"] + year_column}}
    )
    df["count"] = df[year_column].sum(axis=1)
    final_columns = ["company_name", "industry", "city_company", "country/region_company", "annual_revenue",
                     "number_of_employees", "company_id", "number_of_associated_contacts", "count"] + year_column
    df = df.reindex(columns=final_columns)
    df.rename(columns = {'number_of_associated_contacts':'no_of_attendees'}, inplace=True)
    for index, row in df.iterrows():
        for year in year_column:
            if df.at[index, year] == 0:
                df.at[index, year] = ""
    df.columns = df.columns.str.replace("_", " ")
    df_columns = df.columns.to_list()
    df.columns = [x.capitalize() for x in df_columns]
    excel_write_and_save(writer, df, "Comp Company")
    return df

def comp_title_formatting(writer, df, year_column):
    df.columns = [x.lower() for x in df.columns]
    df.columns = [x.replace(' ', '_') for x in df.columns]
    df["annual_revenue"] = df["annual_revenue"].replace('(No value)', 0).astype(float)
    df["number_of_employees"] = df["number_of_employees"].replace('(No value)', 0).astype(float)
    df["year"] = '20' + df["conference_code"].astype(str).str[1:3]
    df["contact_id"] = df["contact_id"].astype(str)
    df["year_and_id"] = df["year"] + df["contact_id"]

    all_columns = df.columns.tolist() + year_column
    df = df.reindex(columns=all_columns)

    for index, row in df.iterrows():
        year = row["year"]
        if year in year_column:
            df.at[index, year] = 1

    df = df.groupby(["contact_id"], as_index=False).agg(
        {**{column: "sum" for column in year_column},
         **{col: "first" for col in df.columns if col not in ["contact_id"] + year_column}}
    )
    df["count"] = df[year_column].sum(axis=1)
    final_columns = ["company_name", "first_name", "last_name", "job_title", "city", "country/region",
                     "management_level", "contact_id", "count"] + year_column
    df = df.reindex(columns=final_columns)
    for index, row in df.iterrows():
        for year in year_column:
            if df.at[index, year] == 0:
                df.at[index, year] = ""
    df.columns = df.columns.str.replace("_", " ")
    df_columns = df.columns.to_list()
    df.columns = [x.capitalize() for x in df_columns]
    excel_write_and_save(writer, df, "Comp Title")
    return df

def company_per_event_formatting(writer, paid_company, comp_company, year_column):
    company_event_paid = paid_company.copy()
    for index, row in company_event_paid.iterrows():
        for year in year_column:
            if company_event_paid.at[index, year] != "":
                company_event_paid.at[index, year] = "paid"
    company_event_comp = comp_company.copy()
    company_event_comp["Amount"] = 0
    for index, row in company_event_comp.iterrows():
        for year in year_column:
            if company_event_comp.at[index, year] != "":
                company_event_comp.at[index, year] = "comp"
    company_event = pd.concat([company_event_paid, company_event_comp], ignore_index=True)
    company_event = company_event.groupby(["Company id"], as_index=False).agg({
        **{"No of attendees": "sum"},
        **{"Amount": "sum"},
        **{column: concat_values for column in year_column},
        **{col: "first" for col in company_event.columns if
           col not in ["Company id", "No of attendees", "Amount"] + year_column}
    })
    for index, row in company_event.iterrows():
        for year in year_column:
            if company_event.at[index, year] == ", ":
                company_event.at[index, year] = ""
            elif company_event.at[index, year] == ", paid":
                company_event.at[index, year] = "paid"
            elif company_event.at[index, year] == ", comp":
                company_event.at[index, year] = "comp"
            elif company_event.at[index, year] == "comp, ":
                company_event.at[index, year] = "comp"
            elif company_event.at[index, year] == "paid, ":
                company_event.at[index, year] = "paid"
    company_event_columns = ["Company name", "Industry", "City company", "Country/region company", "Annual revenue",
                             "Number of employees", "Company id", "No of attendees", "Amount", "Count"] + year_column
    company_event = company_event.reindex(columns=company_event_columns)
    non_empty_counts = company_event[year_column].apply(lambda x: x[x != ""].count(), axis=1)
    company_event["Count"] = non_empty_counts
    company_event = company_event.drop_duplicates()
    excel_write_and_save(writer, company_event, "Company per Event")
    return company_event

def attendee_per_event_formatting(writer, paid_title, comp_title, year_column):
    attendee_event_paid = paid_title.copy()
    for index, row in attendee_event_paid.iterrows():
        for year in year_column:
            if attendee_event_paid.at[index, year] != "":
                attendee_event_paid.at[index, year] = "paid"
    attendee_event_comp = comp_title.copy()
    attendee_event_comp["Amount"] = 0
    for index, row in attendee_event_comp.iterrows():
        for year in year_column:
            if attendee_event_comp.at[index, year] != "":
                attendee_event_comp.at[index, year] = "comp"
    attendee_event = pd.concat([attendee_event_comp, attendee_event_paid], ignore_index=True)
    attendee_event = attendee_event.groupby(["Contact id"], as_index=False).agg({
        **{"Amount": "sum"},
        **{column: concat_values for column in year_column},
        **{col: "first" for col in attendee_event.columns if col not in ["Contact id", "Amount"] + year_column}
    })
    for index, row in attendee_event.iterrows():
        for year in year_column:
            if attendee_event.at[index, year] == ", ":
                attendee_event.at[index, year] = ""
            elif attendee_event.at[index, year] == ", paid":
                attendee_event.at[index, year] = "paid"
            elif attendee_event.at[index, year] == ", comp":
                attendee_event.at[index, year] = "comp"
            elif attendee_event.at[index, year] == "comp, ":
                attendee_event.at[index, year] = "comp"
            elif attendee_event.at[index, year] == "paid, ":
                attendee_event.at[index, year] = "paid"
    attendee_event_columns = ["Company name", "First name", "Last name", "Job title", "City", "Country/region",
                              "Management level", "Contact id", "Amount", "Count"] + year_column
    attendee_event = attendee_event.reindex(columns=attendee_event_columns)
    non_empty_counts = attendee_event[year_column].apply(lambda x: x[x != ""].count(), axis=1)
    attendee_event["Count"] = non_empty_counts
    attendee_event = attendee_event.drop_duplicates()
    excel_write_and_save(writer, attendee_event, "Attendee per Event")
    return attendee_event

def company_compilation_formatting(writer, paid_company, comp_company):
    paid_company.columns = [x.lower() for x in paid_company.columns]
    paid_company.columns = [x.replace(' ', '_') for x in paid_company.columns]
    paid_company["annual_revenue"] = paid_company["annual_revenue"].replace('(No value)', 0).astype(float)
    paid_company["number_of_employees"] = paid_company["number_of_employees"].replace('(No value)', 0).astype(float)
    paid_company["year"] = '20' + paid_company["conference_code"].astype(str).str[1:3]
    paid_company["type"] = "paid"

    comp_company.columns = [x.lower() for x in comp_company.columns]
    comp_company.columns = [x.replace(' ', '_') for x in comp_company.columns]
    comp_company["annual_revenue"] = comp_company["annual_revenue"].replace('(No value)', 0).astype(float)
    comp_company["number_of_employees"] = comp_company["number_of_employees"].replace('(No value)', 0).astype(float)
    comp_company["year"] = '20' + comp_company["conference_code"].astype(str).str[1:3]
    comp_company["type"] = "comp"
    company_compilation = pd.concat([comp_company, paid_company], ignore_index=True)

    company_compilation_col = ['company_name', 'industry', 'city_company', 'country/region_company',
                               'annual_revenue', 'number_of_employees', "conference_code", "year", "type", "company_id"]
    company_compilation = company_compilation[company_compilation_col]
    company_compilation.columns = company_compilation.columns.str.replace("_", " ")
    company_compilation_columns = company_compilation.columns.to_list()
    company_compilation.columns = [x.capitalize() for x in company_compilation_columns]
    company_compilation.drop_duplicates(inplace=True)
    excel_write_and_save(writer, company_compilation, 'Company Compilation')
    return company_compilation

def attendee_compilation_formatting(writer, paid_title, comp_df):
    paid_title.columns = [x.lower() for x in paid_title.columns]
    paid_title.columns = [x.replace(' ', '_') for x in paid_title.columns]
    paid_title["year"] = '20' + paid_title["conference_code"].astype(str).str[1:3]
    paid_title["type"] = "paid"

    comp_df.columns = [x.lower() for x in comp_df.columns]
    comp_df.columns = [x.replace(' ', '_') for x in comp_df.columns]
    comp_df["year"] = '20' + comp_df["conference_code"].astype(str).str[1:3]
    comp_df["type"] = "comp"

    attendee_compilation = pd.concat([comp_df, paid_title], ignore_index=True)
    attendee_compilation_col = ['company_name', 'job_title', 'industry', 'city', 'country/region', 'management_level',
                                'email', 'phone_number', 'year', "conference_code", 'type', 'contact_id']
    attendee_compilation = attendee_compilation[attendee_compilation_col]
    attendee_compilation.columns = attendee_compilation.columns.str.replace("_", " ")
    attendee_compilation_columns = attendee_compilation.columns.to_list()
    attendee_compilation.columns = [x.capitalize() for x in attendee_compilation_columns]
    attendee_compilation = attendee_compilation.drop_duplicates()
    excel_write_and_save(writer, attendee_compilation, 'Attendee Compilation')
    return attendee_compilation

def title_analysis_formatting(writer, attendee_compilation):
    title_analysis = attendee_compilation.groupby("Job title", as_index=False).size()
    title_analysis = title_analysis.rename(columns={'Job title': 'Job title', 'size': 'Count'})
    excel_write_and_save(writer, title_analysis, 'Title Analysis')
    return title_analysis