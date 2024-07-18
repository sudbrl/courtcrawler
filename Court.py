import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import base64
import warnings
from time import sleep

# Ignore warnings for simplicity
warnings.filterwarnings("ignore")

# Define the court list
court_map = {
    'S': {'264': 'सर्वोच्च अदालत'},
    'A': {
        '4': 'जनकपुर', '91': 'जनकपुर, वीरगन्ज', '3': 'जनकपुर, राजविराज', '10': 'तुलसीपुर', 
        '14': 'तुलसीपुर, नेपालगंज', '9': 'तुलसीपुर, बुटवल', '96': 'दिपायल', '13': 'दिपायल, महेन्द्रनगर', 
        '6': 'पाटन', '5': 'पाटन, हेटौंडा', '7': 'पोखरा', '8': 'पोखरा, बाग्लुङ्ग', '1': 'विराटनगर', 
        '90': 'विराटनगर, ओखलढुंगा', '15': 'विराटनगर, इलाम', '2': 'विराटनगर, धनकुटा', '11': 'सुर्खेत', 
        '12': 'सुर्खेत, जुम्ला'
    },
    'D': {
        '33': 'अछाम', '85': 'अर्धाखांची', '43': 'ईलाम', '53': 'उदयपुर', '51': 'ओखलढुंगा', '40': 'कन्चनपुर', 
        '89': 'कपिलवस्तु', '70': 'काठमाण्डौं', '68': 'काभ्रेपलान्चोक', '29': 'कालिकोट', '77': 'कास्की', 
        '35': 'कैलाली', '52': 'खोटांग', '84': 'गुल्मी', '36': 'गोरखा', '61': 'चितवन', '24': 'जाजरकोट', 
        '28': 'जुम्ला', '44': 'झापा', '38': 'डडेलधुरा', '34': 'डोटी', '30': 'डोल्पा', '75': 'तनहुं', 
        '45': 'ताप्लेजुंग', '47': 'तेह्रथुम', '18': 'दाङ', '37': 'दार्चुला', '23': 'दैलेख', '66': 'दोलखा', 
        '49': 'धनकुटा', '57': 'धनुषा', '73': 'धादिंग', '87': 'नवलपरासी', '490': 'नवलपुर', '72': 'नुवाकोट', 
        '83': 'पर्वत', '64': 'पर्सा', '97': 'पांचथर', '86': 'पाल्पा', '19': 'प्युठान', '31': 'बझांग', 
        '42': 'बर्दिया', '41': 'बांके', '82': 'बाग्लुंग', '32': 'बाजुरा', '63': 'बारा', '39': 'बैतडी', 
        '69': 'भक्तपुर', '48': 'भोजपुर', '62': 'मकवानपुर', '80': 'मनांग', '58': 'महोत्तरी', '27': 'मुगु', 
        '79': 'मुस्तांग', '16': 'मोरंग', '81': 'म्याग्दी', '74': 'रसुवा', '65': 'रामेछाप', '22': 'रुकुम', 
        '494': 'रुकुमकोट', '88': 'रुपन्देही', '21': 'रोल्पा', '60': 'रौतहट', '76': 'लमजुङ्ग', '71': 'ललितपुर', 
        '46': 'संखुवासभा', '55': 'सप्तरी', '59': 'सर्लाही', '20': 'सल्यान', '67': 'सिन्धुपाल्चोक', 
        '56': 'सिन्धुली', '54': 'सिराहा', '17': 'सुनसरी', '25': 'सुर्खेत', '50': 'सोलुखुम्बु', 
        '78': 'स्यांग्जा', '26': 'हुम्ला'
    },
    'T': {'116': 'बिषेश अदालत'}
}

court_type_display_map = {
    'S': 'सर्वोच्च अदालत',
    'A': 'उच्च अदालत',
    'D': 'जिल्ला अदालत',
    'T': 'बिषेश अदालत'
}

# Helper function to get court names based on court type
def get_court_names(court_type):
    return court_map.get(court_type, {})

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

# Function to fetch table data from the Supreme Court website
def get_table_data(start_date, end_date, court_type, court_id):
    all_data = []
    date_range = pd.date_range(start=start_date, end=end_date)
    progress = 0
    progress_bar = st.progress(progress)
    
    for faisala_date in date_range:
        progress += 1 / len(date_range)
        progress_bar.progress(progress)
        sleep(0.1)  # Simulate work being done
        
        faisala_date_str = faisala_date.strftime('%Y-%m-%d')
        url = 'https://supremecourt.gov.np/cp/'
        form_data = {
            'court_type': court_type,
            'court_id': court_id,
            'regno': '',
            'darta_date': '',
            'faisala_date': faisala_date_str,
            'submit': ''
        }
        try:
            response = requests.post(url, data=form_data, verify=False)
            response.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        if not table:
            continue

        rows = table.find_all('tr')
        table_data = []
        for row in rows[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            table_data.append(cols)
        all_data.extend(table_data)
    
    progress_bar.empty()
    return all_data

# Validate and process data on button click
if st.button("Generate Report"):
    if not start_date_str or not end_date_str:
        st.warning("Please enter both start and end dates.")
    elif not court_type or not court_id:
        st.warning("Please select both court type and court name.")
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            table_data = get_table_data(start_date, end_date, court_type, court_id)
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
        except ValueError:
            st.error("Invalid date format. Please enter dates in YYYY-MM-DD format.")
