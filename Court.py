import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

st.title('Supreme Court Data Scraper')

def get_table_data(start_date, end_date):
    all_data = []
    date_range = pd.date_range(start=start_date, end=end_date)

    for faisala_date in date_range:
        faisala_date = faisala_date.strftime('%Y-%m-%d')
        url = 'https://supremecourt.gov.np/cp/'
        form_data = {
            'court_type': 'A',
            'court_id': '6',
            'regno': '',
            'darta_date': '',
            'faisala_date': faisala_date,
            'submit': ''
        }

        try:
            response = requests.post(url, data=form_data, verify=False)
            response.raise_for_status()
        except requests.RequestException as e:
            st.error(f"Error accessing the website for date {faisala_date}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')

        if not table:
            st.warning(f"No table found for the date {faisala_date}.")
            continue

        rows = table.find_all('tr')
        table_data = []

        for row in rows[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            table_data.append(cols)

        all_data.extend(table_data)

    return all_data

start_date = st.date_input("Enter the start date", value=datetime(2023, 1, 1))
end_date = st.date_input("Enter the end date", value=datetime(2023, 12, 31))

if st.button("Fetch Data"):
    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        with st.spinner("Fetching data..."):
            table_data = get_table_data(start_date, end_date)
        
        if table_data:
            df = pd.DataFrame(table_data)
            df.columns = ["क्र.सं.", "दर्ता नं.", "मुद्दा नं.", "दर्ता मिति", "मुद्दाको किसिम", "मुद्दाको नाम", "वादी", "प्रतिबादी", "फैसला मिति", "पूर्ण पाठ"]
            st.success("Data fetched successfully!")

            @st.cache
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df(df)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='supreme_court_data.csv',
                mime='text/csv',
            )
        else:
            st.warning("No data found for the given date range.")

