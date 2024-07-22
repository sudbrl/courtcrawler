import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from io import BytesIO

# Function to scrape table data from the Supreme Court website
def get_table_data(start_date, end_date, court_type, court_id):
    all_data = []
    date_range = pd.date_range(start=start_date, end=end_date, freq='10D')  # Interval of 10 days

    for faisala_date in date_range:
        faisala_date = faisala_date.strftime('%Y-%m-%d')
        url = 'https://supremecourt.gov.np/cp/'
        form_data = {
            'court_type': court_type,
            'court_id': court_id,
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

# Streamlit app title
st.title('Supreme Court Data Scraper')

# Court type selection
court_type = st.selectbox('Select Court Type', ['A', 'S', 'D'])
# Court ID selection
court_id = st.selectbox('Select Court ID', ['6', '7', '8', '9'])

# Date inputs in text format
start_date_str = st.text_input("Enter the start date in YYYY-MM-DD format (BS)", value="2080-01-01")
end_date_str = st.text_input("Enter the end date in YYYY-MM-DD format (BS)", value="2080-12-30")

# Fetch data button
if st.button("Fetch Data"):
    try:
        # Parse the input dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Check if the start date is before the end date
        if start_date > end_date:
            st.error("Start date must be before end date.")
        else:
            # Fetch and process the data
            with st.spinner("Fetching data..."):
                table_data = get_table_data(start_date, end_date, court_type, court_id)
            
            if table_data:
                # Create DataFrame from the scraped data
                df = pd.DataFrame(table_data)
                df.columns = ["क्र.सं.", "दर्ता नं.", "मुद्दा नं.", "दर्ता मिति", "मुद्दाको किसिम", "मुद्दाको नाम", "वादी", "प्रतिबादी", "फैसला मिति", "पूर्ण पाठ"]
                st.success("Data fetched successfully!")

                # Function to convert DataFrame to Excel format
                @st.cache_data
                def convert_df_to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                        writer.save()
                    processed_data = output.getvalue()
                    return processed_data

                # Convert the DataFrame to Excel and provide a download button
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="Download data as Excel",
                    data=excel_data,
                    file_name='supreme_court_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
            else:
                st.warning("No data found for the given date range.")
    except ValueError:
        st.error("Invalid date format. Please enter the date in YYYY-MM-DD format (BS).")
