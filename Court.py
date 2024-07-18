import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import base64

# Streamlit UI
st.title('Supreme Court Data Scraper')

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
        '25': 'बारा जिल्ला अदालत',
        '55': 'बार्दिया जिल्ला अदालत',
        '78': 'भक्तपुर जिल्ला अदालत',
        '71': 'भोजपुर जिल्ला अदालत',
        '46': 'मकवानपुर जिल्ला अदालत',
        '67': 'महोत्तरी जिल्ला अदालत',
        '88': 'मोरङ जिल्ला अदालत',
        '69': 'मूलतानी जिल्ला अदालत',
        '27': 'मुगु जिल्ला अदालत',
        '62': 'मुस्ताङ जिल्ला अदालत',
        '26': 'मैल्ला जिल्ला अदालत',
        '59': 'मोरंग जिल्ला अदालत',
        '39': 'रामेछाप जिल्ला अदालत',
        '22': 'रासुवा जिल्ला अदालत',
        '21': 'रौतहट जिल्ला अदालत',
        '74': 'रूपन्देही जिल्ला अदालत',
        '60': 'लालितपुर जिल्ला अदालत',
        '79': 'लमजुंग जिल्ला अदालत',
        '65': 'लिखुपिया जिल्ला अदालत',
        '56': 'वैतडा जिल्ला अदालत',
        '63': 'सप्तरी जिल्ला अदालत',
        '17': 'सर्लाही जिल्ला अदालत',
        '76': 'सिन्धुली जिल्ला अदालत',
        '48': 'सिरहा जिल्ला अदालत',
        '50': 'सोलुखुम्बु जिल्ला अदालत',
        '81': 'सोलुकुम्बु जिल्ला अदालत',
        '80': 'सोलुकुम्बु जिल्ला अदालत',
        '54': 'सुर्खेत जिल्ला अदालत',
        '16': 'स्याङ्जा जिल्ला अदालत',
        '58': 'हुम्ला जिल्ला अदालत',
        '90': 'सागरमाथा जिल्ला अदालत',
        '91': 'अस्थायी इजलास जनकपुर',
        '92': 'अस्थायी इजलास जनकपुर',
        '93': 'अस्थायी इजलास जनकपुर',
        '94': 'अस्थायी इजलास जनकपुर',
        '95': 'अस्थायी इजलास जनकपुर',
        '98': 'अस्थायी इजलास दिपायल',
        '99': 'अस्थायी इजलास पोखरा',
        '100': 'अस्थायी इजलास सुर्खेत'
    }
}

# Function to scrape data
def scrape_supreme_court_data(court_type, court_id):
    url = f'https://www.supremecourt.gov.np/web/{court_type}/{court_id}/'
    with st.spinner(f'Scraping data from {court_map[court_type][court_id]}...'):
        response = requests.get(url, verify=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            data_table = soup.find('table')
            if data_table:
                # Parse HTML table into DataFrame
                df = pd.read_html(str(data_table))[0]
                return df
    return None

# Function to generate Excel report
def generate_excel_report(dataframes):
    with st.spinner('Generating Excel report...'):
        with pd.ExcelWriter('supreme_court_data.xlsx') as writer:
            for court_type, courts in dataframes.items():
                for court_id, df in courts.items():
                    sheet_name = f'{court_map[court_type][court_id]}'
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

# Main app logic
def main():
    court_type = st.selectbox('Select Court Type', list(court_map.keys()))
    court_ids = court_map[court_type]
    court_id = st.selectbox('Select Court', list(court_ids.keys()))

    if st.button('Scrape Data'):
        data = scrape_supreme_court_data(court_type, court_id)
        
        if data is not None:
            st.write('Data scraped successfully!')
            st.write(data.head())  # Displaying first few rows of data
            dataframes = {court_type: {court_id: data}}
            generate_excel_report(dataframes)
            st.success('Excel report generated. Click below to download.')

            # Create download link for the Excel file
            excel_file = open('supreme_court_data.xlsx', 'rb').read()
            b64 = base64.b64encode(excel_file).decode()
            href = f'<a href="data:file/xlsx;base64,{b64}" download="supreme_court_data.xlsx">Download Excel File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.error('Failed to scrape data. Please try again.')

if __name__ == "__main__":
    main()
