import google.auth
import google.auth.transport.requests
import requests
import streamlit as st
import pandas as pd
import time

from pandas import json_normalize

# Function to get Google Cloud access token using service account
def get_gcloud_access_token():
    creds, project = google.auth.default()

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token

# Function to make an API call with pagination
def get_results(base_url, query):
    access_token = get_gcloud_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "pageSize": 10,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"}
    }

    pageToken = None
    all_items = []

    while True:
        if pageToken:
            response = requests.post(
                base_url + "?pageToken=" + pageToken,
                headers=headers,
                json=data
            )
        else:
            response = requests.post(
                base_url,
                headers=headers,
                json=data
            )
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}")
        response_json = response.json()
        items = response_json.get('results', [])
        all_items.extend(items)

        pageToken = response_json.get('nextPageToken', None)
        time.sleep(1)  # rate limiting
        if not pageToken:
            break

    return all_items

# Render Streamlit results (header + table)
def render_results(subheader, results):
    st.subheader(subheader)
    df = json_normalize(results, sep=' ')
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No data found.")
    return df


def main():
    st.title("Data Warehouse Search Interface")
    query = st.text_input("Enter your data warehouse query, using natural language")

    if st.button("Search"):
        if query:
            results = get_results(
                YOUR_ENDPOINT_HERE,
                query
            )
            render_results("Nature Results", results)
            results = get_results(
                YOUR_ENDPOINT_HERE,
                query
            )
            render_results("Arxiv Results", results)
        else:
            st.write("Please enter a search query.")

if __name__ == "__main__":
    main()