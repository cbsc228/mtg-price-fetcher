# -*- coding: utf-8 -*-

# Import required methods
#from requests import get
import mariadb
import sys
import requests
from itertools import batched
from time import sleep
import pandas as pd
import datetime

def add_id_to_list(lst):
    json_list = []
    for obj in enumerate(lst):
        json_obj = {"id": obj[1]}
        json_list.append(json_obj)
    return json_list

#api request header for scryfall services as required by their documentation
headers = {'User-Agent': 'market_price_fetcher/1.0', 'Accept': 'application/json'}

#connect to local database hosted on separate raspberry pi
try:
    conn = mariadb.connect(
        user="/USERNAME/",
        password="/PASSWORD/",
        host="/HOSTNAME",
        port=3306,
        database="mtg_collection"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get a cursor object to execute queries
cur = conn.cursor()

#SQL query to pull cards that need price checks
cur.execute("SELECT scryfall_id FROM cards;")

# Fetch all results and remove duplicates
results = cur.fetchall()
results_cleaned = []
[results_cleaned.append(x) for x in results if x not in results_cleaned]

#process results_cleaned
'''
Make queries to scryfall api from results_cleaned variable and store for processing.
DOUBLE CHECK API RULES FROM SCRYFALL!!!
'''
#the max number of cards that can be requsted at a time from the Scryfall API
batch_size = 75
#column index of the results_cleaned variable that contains the scryfall IDs necessary to request from the API
column_index = 0
#counter for debugging purposes
iteration = 0
cards_to_process = []
for batch in batched(results_cleaned, batch_size):
    #get all scryfall IDs in current batch
    scryfall_id_batch = [row[column_index] for row in batch]
    #generate a list of 'ID' tags to append to scryfall id list to match required API JSON syntax
    scryfall_id_batch = add_id_to_list(scryfall_id_batch)
    #append the two pieces and create request
    collection_request = {"identifiers": scryfall_id_batch}
    #make request to scryfall API using required headers per their documentation, making sure to limit request speed to no more than 10 per second
    response = requests.post("https://api.scryfall.com/cards/collection", json=collection_request, headers=headers)
    sleep(0.1)
    #convert response to JSON format
    cards = response.json()
    #append this batch of cards to the total list that will be uploaded to the database
    cards_to_process.append(cards['data'])
    #temporary for debugging purposes
    iteration += 1
    print("Batch number", iteration, 'pulled successfully')

#pull required data from JSON batch list
prices_to_upload = pd.DataFrame()
#Get a batch of cards, each batch is a maximum of 75 cards
for batch in cards_to_process:
    #process each card individually in the batch
    for item in batch:
        #append the card prices to the dataframe, using it's scryfall ID as the index;
        prices_to_upload = pd.concat([prices_to_upload, pd.DataFrame(item['prices'], index=[item['id']])], axis=0)

#add the date of price check to each card
prices_to_upload['date'] = datetime.date.today()
#moves index into a column
prices_to_upload = prices_to_upload.reset_index()

#upload prices into the price history database while ignore any duplicate entires
try:
    cur.executemany(
        "INSERT IGNORE INTO price_history (scryfall_id, usd, usd_foil, usd_etched, eur, eur_foil, tix, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        prices_to_upload.to_numpy().tolist()
    )
    conn.commit()
    print("Price history successfully updated")
except mariadb.Error as e:
    print(f"Error: {e}")


# Close the cursor and connection
cur.close()
conn.close()
