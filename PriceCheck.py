import urllib.request
from coinbase.wallet.client import Client
import json

client = Client("ju5AObXiPXwhTFsc", "MOPPyWy89dB4RhmvCvbPDfMNXLeNEfnr")

txn = client.get_transactions("267b5bd3-8bba-5d88-851c-e2e88b9772d0")
print(txn)
"""
time = txn.data[0].created_at[0:10] + "T00%3A00%3A00Z"

url = "https://api.nomics.com/v1/currencies/sparkline?key=2baa6243a49438a70af105695e3e951f&ids=" + txn.data[0].amount.currency + "&start=" + time + "&end=" + time

coinPrice = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))[0]

print(coinPrice)

print(coinPrice.keys())

cost = float(txn.data[0].amount.amount) * float(coinPrice["prices"][0])

print("API price:" + coinPrice["prices"][0] + " Coinbase Price:" + str(float(txn.data[0].native_amount.amount)/float(txn.data[0].amount.amount)))

print(cost)"""