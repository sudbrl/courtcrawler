import asyncio
import aiohttp
import ssl
import certifi
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to fetch data from the server
async def fetch_data(session, url, form_data):
    retries = 3
    for attempt in range(retries):
        try:
            logging.info(f"Attempt {attempt + 1}: Fetching data from {url}")
            async with session.post(url, data=form_data, ssl=ssl.create_default_context(cafile=certifi.where())) as response:
                response.raise_for_status()  # Raise an error for bad status
                data = await response.text()
                logging.info(f"Data fetched successfully on attempt {attempt + 1}")
                return data
        except aiohttp.ClientConnectorError as e:
            logging.error(f"ClientConnectorError: {e}")
            if attempt < retries - 1:
                logging.info("Retrying...")
                await asyncio.sleep(1)
            else:
                raise
        except aiohttp.ClientError as e:
            logging.error(f"ClientError: {e}")
            raise

# Function to get table data
async def get_table_data(start_date, end_date, court_type, court_id):
    url = "https://example.com/api"  # Replace with the actual URL
    form_data = {
        "start_date": start_date,
        "end_date": end_date,
        "court_type": court_type,
        "court_id": court_id
    }

    async with aiohttp.ClientSession() as session:
        data = await fetch_data(session, url, form_data)
        return data

def main():
    start_date = "2081-04-03"  # Example start date in BS format
    end_date = "2081-04-03"  # Example end date in BS format
    court_type = "सर्वोच्च अदालत"
    court_id = "some_court_id"  # Replace with the actual court ID

    loop = asyncio.get_event_loop()
    try:
        table_data = loop.run_until_complete(get_table_data(start_date, end_date, court_type, court_id))
        logging.info(f"Table Data: {table_data}")
        # Here you can process the table_data further or save it to a file
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
