import streamlit as st
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import base64


# Define the court list
court_map = {
    'S': {'264': 'सर्वोच्च अदालत'},
    'A': {
        '4': 'उच्च अदालत जनकपुर',
        '91': 'उच्च अदालत जनकपुर, अस्थायी इजलास वीरगन्ज',
        '3': 'उच्च अदालत जनकपुर, राजविराज इजलास',
        '10': 'उच्च अदालत तुलसीपुर',
        '14': 'उच्च अदालत तुलसीपुर, नेपालगंज इजलास',
        '9': 'उच्च अदालत तुलसीपुर, बुटवल इजलास',
        '96': 'उच्च अदालत दिपायल',
        '13': 'उच्च अदालत दिपायल, महेन्द्रनगर इजलास',
        '6': 'उच्च अदालत पाटन',
        '5': 'उच्च अदालत पाटन, हेटौंडा इजलास',
        '7': 'उच्च अदालत पोखरा',
        '8': 'उच्च अदालत पोखरा, बाग्लुङ्ग इजलास',
        '1': 'उच्च अदालत विराटनगर',
        '90': 'उच्च अदालत विराटनगर, अस्थायी इजलास ओखलढुंगा',
        '15': 'उच्च अदालत विराटनगर, इलाम इजलास',
        '2': 'उच्च अदालत विराटनगर, धनकुटा इजलास',
        '11': 'उच्च अदालत सुर्खेत',
        '12': 'उच्च अदालत सुर्खेत, जुम्ला इजलास'
    },
    'D': {
        '33': 'अछाम जिल्ला अदालत',
        '85': 'अर्धाखांची जिल्ला अदालत',
        '43': 'ईलाम जिल्ला अदालत',
        '53': 'उदयपुर जिल्ला अदालत',
        '51': 'ओखलढुंगा जिल्ला अदालत',
        '40': 'कन्चनपुर जिल्ला अदालत',
        '89': 'कपिलवस्तु जिल्ला अदालत',
        '70': 'काठमाण्डौं जिल्ला अदालत',
        '68': 'काभ्रेपलान्चोक जिल्ला अदालत',
        '29': 'कालिकोट जिल्ला अदालत',
        '77': 'कास्की जिल्ला अदालत',
        '35': 'कैलाली जिल्ला अदालत',
        '52': 'खोटांग जिल्ला अदालत',
        '84': 'गुल्मी जिल्ला अदालत',
        '36': 'गोरखा जिल्ला अदालत',
        '61': 'चितवन जिल्ला अदालत',
        '24': 'जाजरकोट जिल्ला अदालत',
        '28': 'जुम्ला जिल्ला अदालत',
        '44': 'झापा जिल्ला अदालत',
        '38': 'डडेलधुरा जिल्ला अदालत',
        '34': 'डोटी जिल्ला अदालत',
        '30': 'डोल्पा जिल्ला अदालत',
        '75': 'तनहुं जिल्ला अदालत',
        '45': 'ताप्लेजुंग जिल्ला अदालत',
        '47': 'तेह्रथुम जिल्ला अदालत',
        '18': 'दाङ जिल्ला अदालत',
        '37': 'दार्चुला जिल्ला अदालत',
        '23': 'दैलेख जिल्ला अदालत',
        '66': 'दोलखा जिल्ला अदालत',
        '49': 'धनकुटा जिल्ला अदालत',
        '57': 'धनुषा जिल्ला अदालत',
        '73': 'धादिंग जिल्ला अदालत',
        '87': 'नवलपरासी जिल्ला अदालत',
        '490': 'नवलपुर जिल्ला अदालत',
        '72': 'नुवाकोट जिल्ला अदालत',
        '83': 'पर्वत जिल्ला अदालत',
        '64': 'पर्सा जिल्ला अदालत',
        '97': 'पांचथर जिल्ला अदालत',
        '86': 'पाल्पा जिल्ला अदालत',
        '19': 'प्युठान जिल्ला अदालत',
        '31': 'बझांग जिल्ला अदालत',
        '42': 'बर्दिया जिल्ला अदालत',
        '41': 'बांके जिल्ला अदालत',
        '82': 'बाग्लुंग जिल्ला अदालत',
        '32': 'बाजुरा जिल्ला अदालत',
        '63': 'बारा जिल्ला अदालत',
        '39': 'बैतडी जिल्ला अदालत',
        '69': 'भक्तपुर जिल्ला अदालत',
        '48': 'भोजपुर जिल्ला अदालत',
        '62': 'मकवानपुर जिल्ला अदालत',
        '80': 'मनांग जिल्ला अदालत',
        '58': 'महोत्तरी जिल्ला अदालत',
        '27': 'मुगु जिल्ला अदालत',
        '79': 'मुस्तांग जिल्ला अदालत',
        '16': 'मोरंग जिल्ला अदालत',
        '81': 'म्याग्दी जिल्ला अदालत',
        '74': 'रसुवा जिल्ला अदालत',
        '65': 'रामेछाप जिल्ला अदालत',
        '22': 'रुकुम जिल्ला अदालत',
        '494': 'रुकुमकोट जिल्ला अदालत',
        '88': 'रुपन्देही जिल्ला अदालत',
        '21': 'रोल्पा जिल्ला अदालत',
        '60': 'रौतहट जिल्ला अदालत',
        '76': 'लमजुङ्ग जिल्ला अदालत',
        '71': 'ललितपुर जिल्ला अदालत',
        '46': 'संखुवासभा जिल्ला अदालत',
        '55': 'सप्तरी जिल्ला अदालत',
        '59': 'सर्लाही जिल्ला अदालत',
        '20': 'सल्यान जिल्ला अदालत',
        '67': 'सिन्धुपाल्चोक जिल्ला अदालत',
        '56': 'सिन्धुली जिल्ला अदालत',
        '54': 'सिराहा जिल्ला अदालत',
        '17': 'सुनसरी जिल्ला अदालत',
        '25': 'सुर्खेत जिल्ला अदालत',
        '50': 'सोलुखुम्बु जिल्ला अदालत',
        '78': 'स्यांग्जा जिल्ला अदालत',
        '26': 'हुम्ला जिल्ला अदालत'
    },
    'T': {'116': 'बिषेश अदालत'}
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
