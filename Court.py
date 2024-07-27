import streamlit as st
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import base64
import warnings
import ssl
import os

# Ignore warnings for simplicity
warnings.filterwarnings("ignore")

# Define the court list
court_map = {
    'S': {
        '264': 'सर्वोच्च अदालत'
    },
    'A': {
        '4': 'उच्च अदालत जनकपुर',
        # (Other courts omitted for brevity)
    },
    'D': {
        '33': 'अछाम जिल्ला अदालत',
        # (Other courts omitted for brevity)
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
    url = 'https://supremecourt.gov.np/cp/'
    form_data = {
        'court_type': court_type,
        'court_id': court_id,
        'regno': '',
        'darta_date': '',
        'faisala_date': date,
        'submit': ''
    }
    
    # Ensure the SSL certificate file exists
    pem_file = 'supreme_court.pem'
    if not os.path.isfile(pem_file):
        raise FileNotFoundError(f"{pem_file} not found")

    ssl_context = ssl.create_default_context(cafile=pem_file)
    async with session.post(url, data=form_data, ssl=ssl_context) as response:
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
        try:
            with st.spinner("Fetching data..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                table_data = loop.run_until_complete(get_table_data(start_date_str, end_date_str, court_type, court_id))

            if table_data:
                df = pd.DataFrame(table_data)
                df.columns = ["क्र.सं.", "दर्ता नं.", "मुद्दा नं.", "दर्ता मिति", "मुद्दाको किसिम", "मुद्दाको नाम", "वादी", "प्रतिबादी", "फैसला मिति", "पूर्ण पाठ"]
                excel_file_path = "supreme_court_data.xlsx"
                df.to_excel(excel_file_path, index=False)
                with open(excel_file_path, 'rb') as f:
                    excel_bytes = f.read()
                b64 = base64.b64encode(excel_bytes).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="court_data.xlsx">Download Excel file</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("No data found for the specified date range and court parameters.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
