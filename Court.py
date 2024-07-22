import streamlit as st
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import base64

# Define the court list
court_map = {
    'S': {
        '264': 'सर्वोच्च अदालत'
    },
    'A': {
        '4': 'उच्च अदालत जनकपुर',
        #...
    },
    'D': {
        '33': 'अछाम जिल्ला अदालत',
        #...
    },
    'T': {
        '116': 'बिषेश अदालत'
    }
}

# Mapping for display names
court_type_display_map = {
    'S': 'सर्वोच्च अदालत',
    'A': 'उच्च अदालत',
    'D': 'जिल्ला अदालत',
    'T': 'बिषेश अदालत'
}

# Helper function to get court names based on court type
def get_court_names(court_type):
    if court_type in court_map:
        return court_map[court_type]
    return {}

# Streamlit UI
st.title('Supreme Court Data Scraper')

# Input fields for start date, end date, court type, and court ID
start_date_str = st.text_input("Enter Start Date (YYYY-MM-DD, BS)")
end_date_str = st.text_input("Enter End Date (YYYY-MM-DD, BS)")

court_type_display = st.selectbox("Select Court Type", options=list(court_type_display_map.values()))

# Get the actual court type key based on display name
court_type = [key for key, value in court_type_display_map.items() if value == court_type_display][0]

# Display court names based on selected court type
court_names = get_court_names(court_type)
court_name_to_id = {v: k for k, v in court_names.items()}
court_name = st.selectbox("Select Court Name", options=list(court_name_to_id.keys()))
court_id = court_name_to_id[court_name] if court_name else None

# Function to fetch table data from the Supreme Court website asynchronously
async def fetch_data(session, date, court_type, court_id):
    try:
        url = 'https://supremecourt.gov.np/cp/'
        form_data = {
            'court_type': court_type,
            'court_id': court_id,
            'egno': '',
            'darta_date': '',
            'faisala_date': date,
            'ubmit': ''
        }
        async with session.post(url, data=form_data) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                table = soup.find('table')
                if table:
                    rows = table.find_all('tr')
                    table_data = []
                    for row in rows[1:]:
                        cols = row.find_all('td')
                        cols = [col.text.strip() for col in cols]
                        table_data.append(cols)
                    return table_data
            return []
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

async def get_table_data(start_date, end_date, court_type, court_id):
    async with aiohttp.ClientSession() as session:
        tasks = []
        date_range = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
        for faisala_date in date_range:
            tasks.append(fetch_data(session, faisala_date, court_type, court_id))
        results = await asyncio.gather(*tasks)
        all_data = [item for sublist in results for item in sublist]
        return all_data

# Validate and process data on button click
if st.button("Generate Report"):
    if not start_date_str or not end_date_str:
        st.warning("Please enter both start and end dates.")
    elif not court_type or not court_id:
        st.warning("Please select both court type and court name.")
    else:
        try
