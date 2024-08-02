# pylint: disable-msg=C0103
"""
    Get all AAVE V2 borrow transactions from The Graph
"""
import csv
import requests
import os

keys, transactions = None, []
current_time = 1722482066
START_TIME = 1654016400
last_transactions = set()

API_KEY = os.getenv("API_KEY")

while True:
    query = """
    {
        borrows(where: {timestamp_lte: """ + str(current_time) + """, timestamp_gt: """ + START_TIME + """}, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            user {
                id
            }
            caller {
                id
            }
            reserve {
                symbol
            }
            amount
            borrowRate
            borrowRateMode
            timestamp
            stableTokenDebt
            variableTokenDebt
        }
    }
    """
    response = requests.post("https://gateway-arbitrum.network.thegraph.com/api/" + API_KEY + "/subgraphs/id/8wR23o1zkS4gpLqLNU4kG3JHYVucqGyopL5utGxP2q1N",
                             '',
                             json={'query': query})
    if response.status_code != 200:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
        continue
    try:
        data = response.json()["data"]["borrows"]
    except Exception:
        print("Error at timestamp", current_time)
        continue
    if len(data) == 0:
        break
    if keys is None:
        keys = data[0].keys()
    index = 0
    try:
        while data[index]["id"] in last_transactions:
            index += 1
    except IndexError:
            current_time -= 1
            continue
    print(len(data) - index, "transactions found at timestamp", current_time)
    for transaction in data[index:]:
        transaction["user"] = transaction["user"]["id"]
        transaction["reserve"] = transaction["reserve"]["symbol"]
        transaction["caller"] = transaction["caller"]["id"]
        transactions.append(transaction)
    current_time = int(data[-1]["timestamp"])
    index = -1
    last_transactions = set()
    while data[index]["timestamp"] == data[-1]["timestamp"]:
        last_transactions.add(data[index]["id"])
        index -= 1

with open('borrow.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(transactions)
