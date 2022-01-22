from coinbase.wallet.client import Client as CBClient
import cbpro as CBPClient
from binance.client import Client as BClient
from okex import account_api as OKExClient
import csv
import re
import time
from calendar import timegm
import os
import urllib.request
import json
import datetime


def makeCoinBaseCSV(fileName="CSV/CoinBase.csv"):

    csvFile = csv.DictWriter(open(fileName, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income","Purchase"])
    csvFile.writeheader()

    client = CBClient("CoinBase", "API Key")

    accounts = client.get_accounts(limit=100)

    for acc in accounts.data:

        txns = client.get_transactions(acc.id, limit=100).data

        txns.reverse()

        for txn in txns:
            utc_time = time.strptime(txn.created_at, "%Y-%m-%dT%H:%M:%SZ")
            timeStamp = timegm(utc_time)
            csvFile.writerow({"Coin": txn.amount.currency, "AmountCoin" : ("-" + txn.network.transaction_amount.amount) if hasattr(txn, "network") and hasattr(txn.network, "transaction_fee") else txn.amount.amount, "Timestamp" : timeStamp, "Description" : txn.details.title + " " + txn.details.subtitle, "Income" : "0" if txn.details.title.find("Received") == -1 else "1", "Purchase" : "1" if (txn.amount.currency == "LTC" and txn.details.title.find("Received") != -1) else "0", "Date" : txn.created_at})
            if hasattr(txn, "network") and hasattr(txn.network, "transaction_fee"):
                csvFile.writerow({"Coin": txn.network.transaction_fee.currency, "AmountCoin" : "-" + txn.network.transaction_fee.amount, "Timestamp" : timeStamp, "Description" : "Fee from " + txn.details.title + " " + txn.details.subtitle, "Income" : "0", "Purchase" : "0", "Date" : txn.created_at})
                

def makeCoinBaseProCSV(fileName="CSV/CoinBasePro.csv"):
    
    csvFile = csv.DictWriter(open(fileName, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income", "Purchase"])
    csvFile.writeheader()

    client = CBPClient.AuthenticatedClient("CoinBase" , "Pro", "API Key")

    accounts = client.get_accounts()

    for acc in accounts:

        txns = client.get_account_history(acc["id"], limit=100)

        for txn in txns:
            if not isinstance(txn, str):
                timeStamp = txn["created_at"][:19] + "Z"
                utc_time = time.strptime(timeStamp, "%Y-%m-%dT%H:%M:%SZ")
                timeStamp = timegm(utc_time)
                csvFile.writerow({"Coin": acc["currency"], "AmountCoin" : txn["amount"], "Timestamp" : timeStamp, "Description" : txn["type"] + (" " + txn["details"]["product_id"] if txn["type"] != "transfer" else ""), "Income" : "0", "Purchase" : "0", "Date" : txn["created_at"][:19] + "Z"})

def makeBinanceCSVFromTotalStatement(fileNameIn="CSVIn/BinanceTotalStatement.csv", fileNameOut="CSV/BinanceFromTotalStatement.csv"):
    csvIn = csv.DictReader(open(fileNameIn, newline=''))
    csvFile = csv.DictWriter(open(fileNameOut, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income","Purchase"])
    csvFile.writeheader()

    for row in csvIn:
        if row["Operation"].find("avings purchase") == -1 and row["Operation"].find("redemption") == -1:
            timestamp = timegm(time.strptime(row["UTC_Time"], "%Y-%m-%d %H:%M"))
            isIncome = row["Operation"].find("interest") != -1 or row["Operation"].find("mining") != -1 or row["Operation"].find("Distribution") != -1
            csvFile.writerow({"Coin" : row["Coin"], "AmountCoin" : row["Change"], "Timestamp" : timestamp, "Description" : row["Operation"] if isIncome else "1", "Income" : "1" if isIncome else "0", "Purchase" : "1" if row["Remark"].find("Purchase") != -1 else "0", "Date" : row["UTC_Time"].replace(" ", "T") + "Z"})


def makeBinanceCSVFromCSV(fileNameIn="C:/Users/BenPC/Downloads/Export Recent Trade History.csv", fileNameOut="CSV/BinanceTradesFromCSV.csv"):
    csvIn = csv.DictReader(open(fileNameIn, newline=''))
    csvFile = csv.DictWriter(open(fileNameOut, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income","Purchase"])
    csvFile.writeheader()

    for row in csvIn:
        
        secondCoin = ""
        USDtrade = False
        if row["Market"].endswith("BUSD"):
            secondCoin = "BUSD"
            USDtrade = True
        elif row["Market"].endswith("USDT"):
            secondCoin = "USDT"
            USDtrade = True
        elif row["Market"].endswith("BTC"):
            secondCoin = "BTC"
        elif row["Market"].endswith("BNB"):
            secondCoin = "BNB"
        elif row["Market"].endswith("ETH"):
            secondCoin = "ETH"
        elif row["Market"].endswith("TRX"):
            secondCoin = "TRX"
        elif row["Market"].endswith("XRP"):
            secondCoin = "XRP"
        elif row["Market"].endswith("USDC"):
            secondCoin = "USDC"
            USDtrade = True
        elif row["Market"].endswith("DAI"):
            secondCoin = "DAI"
            USDtrade = True
        else:
            secondCoin = input("Coin error, please enter the right most coin, " + row["Market"])
        firstCoin = row["Market"][:len(row["Market"])-len(secondCoin)]

        timeStamp = row["ï»¿Date(UTC)"]

        if len(timeStamp) == 15:
            timeStamp = timeStamp.replace(" ", "T0")
        else:
            timeStamp = timeStamp.replace(" ", "T")
        
        timeStamp = timeStamp + ":00Z"

        utc_time = time.strptime(timeStamp, "%Y-%m-%dT%H:%M:%SZ")
        timeStamp = timegm(utc_time)

        fc = "-"
        sc = ""

        if row["Type"] == "BUY":
            fc = ""
            sc = "-"

        csvFile.writerow({"Coin" : firstCoin, "AmountCoin" : fc+row["Amount"], "Timestamp" : timeStamp, "Description" : row["Market"] if USDtrade else "1", "Income" : "0"})
        csvFile.writerow({"Coin" : secondCoin, "AmountCoin" : sc+row["Total"], "Timestamp" : timeStamp, "Description" : row["Market"] if USDtrade else "1", "Income" : "0"})
        if row["Fee"] != "0":
            csvFile.writerow({"Coin" : row["Fee Coin"], "AmountCoin" : "-" + row["Fee"], "Timestamp" : timeStamp, "Description" : "This is the fee from " + row["Market"], "Income" : "0"})

def makeBinanceCSVNotTrades(fileName="CSV/BinanceNotTrades.csv"):
    csvFile = csv.DictWriter(open(fileName, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income","Purchase"])
    csvFile.writeheader()
    
    client = BClient("Binance Key Here", "Binance Key Here")
    
    curPage = 1
    lendingTypes = ["DAILY", "ACTIVITY", "CUSTOMIZED_FIXED"]
    lendingIndex = 0
    while lendingIndex < len(lendingTypes):
        while True:
            interestHistory = client.get_lending_interest_history(lendingType=lendingTypes[lendingIndex], size=100, current=curPage)
            if interestHistory == []:
                break
            for row in interestHistory:
                csvFile.writerow({"Coin" : row["asset"], "AmountCoin" :  row["interest"], "Timestamp" : int(row["time"]/1000), "Description" : "Income from " + lendingTypes[lendingIndex], "Income" : "1"})
            curPage += 1
        lendingIndex += 1
    
    depositHistory = client.get_deposit_history()

    for row in depositHistory["depositList"]:
        csvFile.writerow({"Coin" : row["asset"], "AmountCoin" :  row["amount"], "Timestamp" : int(row["insertTime"]/1000), "Description" : "Transfered to Binance", "Income" : "0"})

    withdrawHistory = client.get_withdraw_history()

    for row in withdrawHistory["withdrawList"]:
        csvFile.writerow({"Coin" : row["asset"], "AmountCoin" :  "-" + str(row["amount"]), "Timestamp" : int(row["applyTime"]/1000), "Description" : "Transfered from Binance", "Income" : "0"})
        csvFile.writerow({"Coin" : row["asset"], "AmountCoin" :  "-" + str(row["transactionFee"]), "Timestamp" : int(row["applyTime"]/1000), "Description" : "Transfered from Binance", "Income" : "0"})

def makeOKExCSV(fileNameIn="CSVIn/OKExTransactions.csv", fileNameOut="CSV/OKEx.csv"):
    csvIn = csv.DictReader(open(fileNameIn, newline=''))
    csvFile = csv.DictWriter(open(fileNameOut, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income","Purchase"])
    csvFile.writeheader()

    for row in csvIn:
        utc_time = time.strptime(row["ï»¿Time"], "%Y-%m-%dT%H:%M:%SZ")
        timeStamp = timegm(utc_time)
        csvFile.writerow({"Coin" : row["Coin"], "AmountCoin" :  row["Amount"], "Timestamp" : timeStamp, "Date" : row["ï»¿Time"], "Description" : row["Desc"], "Income" : "1" if row["Desc"] == "Income" else "0", "Purchase" : "1" if row["Desc"] == "Purchase" else "0"})

def combineAndSortCSV(dir="CSV", fileNameOut="AllTransactionsSorted.csv"):

    arr = []

    for fileName in os.listdir(dir):
        csvIn = csv.DictReader(open(dir+"/"+fileName, newline=''))
        for row in csvIn:
            arr.append(row)
    
    arr = sorted(arr, key=lambda row : int(row["Timestamp"]))

    csvFile = csv.DictWriter(open(fileNameOut, 'w', newline=''), fieldnames=["Coin", "AmountCoin", "Timestamp","Date", "Description", "Income", "Purchase"])
    csvFile.writeheader()

    for row in arr:
        csvFile.writerow(row)

def getHistory(JSONOut="Wallet.json", directory="CSV", fileName="AllTransactionsSorted.csv", timestampStart=0, timestampEnd=int(time.time()), sort=False, getPrices=False):
    wallet = {"TotalCADIn" : 0, "CurCAD" : 0, "TotalPurchased" : 0, "TotalIncome" : 0, "TotalACB" : 0, "CapitalGains" : 0, "StartDate" : "", "EndDate" : "", "Coins" : {}}
    if sort:
        combineAndSortCSV(dir=directory, fileNameOut=fileName)
    csvIn = csv.DictReader(open(fileName, newline=''))

    days = {}
    if getPrices:
        days = splitIntoDays(csvIn, timestampStart, timestampEnd)

        for day in days:
            prices = getPricesDay(day, days[day])
            for coin in days[day]:
                for txn in days[day][coin]:
                    if not txn["Coin"] in prices:
                        print("Price not found for " + txn["Coin"])
                        txn["AmountCAD"] = 0
                    else:
                        txn["AmountCAD"] = float(txn["AmountCoin"]) * float(prices[txn["Coin"]])
        json.dump(days, open("WithPrices.json", 'w'))
    else:
        days = json.load(open("WithPrices.json"))
    
    first = True

    for day in days:
        if first:
            wallet["StartDate"] = day
            first = False
        wallet["EndDate"] = day
        dayInInt = timegm(time.strptime(day, "%Y-%m-%d"))
        if dayInInt <= timestampEnd and dayInInt >= timestampStart:
            for coin in days[day]:
                for row in days[day][coin]:
                    if row["Purchase"] == "1":
                        wallet["TotalPurchased"] += row["AmountCAD"]
                    if row["Income"] == "1":
                        wallet["TotalIncome"] += row["AmountCAD"]
                    if not row["Coin"] in wallet["Coins"]:
                        wallet["Coins"][row["Coin"]] = {"AmountCoin" : 0, "AmountACB" : 0, "CapitalGain" : 0}
                    if row["AmountCAD"] < 0:
                        if wallet["Coins"][row["Coin"]]["AmountCoin"] <= 0:
                            print("Sell Error " + str(row))
                            continue
                        wallet["Coins"][row["Coin"]]["CapitalGain"] += -1*row["AmountCAD"]+((wallet["Coins"][row["Coin"]]["AmountACB"]/wallet["Coins"][row["Coin"]]["AmountCoin"])*float(row["AmountCoin"]))
                        wallet["Coins"][row["Coin"]]["AmountACB"] *= (wallet["Coins"][row["Coin"]]["AmountCoin"]+float(row["AmountCoin"]))/wallet["Coins"][row["Coin"]]["AmountCoin"]
                        wallet["Coins"][row["Coin"]]["AmountCoin"] += float(row["AmountCoin"])
                        if wallet["Coins"][row["Coin"]]["AmountCoin"] < 0.000000001:
                            wallet["Coins"][row["Coin"]]["AmountACB"] = 0
                            wallet["Coins"][row["Coin"]]["AmountCoin"] = 0
                    else:
                        wallet["Coins"][row["Coin"]]["AmountCoin"] += float(row["AmountCoin"])
                        wallet["Coins"][row["Coin"]]["AmountACB"] += row["AmountCAD"]
    
    pricesToday = getPricesDay(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d'), wallet["Coins"])

    for coin in wallet["Coins"]:
        wallet["Coins"][coin]["CurrentValue"] = wallet["Coins"][coin]["AmountCoin"]*float(pricesToday[coin])
        wallet["CurCAD"] += wallet["Coins"][coin]["CurrentValue"]
        wallet["CapitalGains"] += wallet["Coins"][coin]["CapitalGain"]
        wallet["TotalACB"] += wallet["Coins"][coin]["AmountACB"]
    wallet["TotalCADIn"] = wallet["TotalPurchased"] + wallet["TotalIncome"]

    with open(JSONOut, 'w') as fp:
        json.dump(wallet, fp)
        
def getPriceUSD(row): #old single use, takes 1 sec per check
    
    timestamp = datetime.datetime.fromtimestamp(int(row["Timestamp"])).strftime('%Y-%m-%dT') + "00%3A00%3A00Z"
    #timestamp = timestamp.replace(":", "%3A")
    coinName = row["Coin"]
    url = "https://api.nomics.com/v1/currencies/sparkline?key=2baa6243a49438a70af105695e3e951f&ids=" + coinName + "&start=" + timestamp + "&end=" + timestamp

    coinPrice = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    print(coinPrice)
    if coinPrice == []:
        return float(input("Coin Price Error, Please input the float price of " + row["Coin"] + " at " + timestamp.replace("%3A", ":") + ": "))
    time.sleep(1)
    return float(coinPrice[0]["prices"][0])

def getPricesCoin(coin): #For All transactions with a single Coin, takes 1 sec per check
    
    timeStart = coin[0]["Date"][0:11]+"00%3A00%3A00Z"
    timeEnd = coin[50]["Date"][0:11]+"00%3A00%3A00Z"
    coinName = coin[0]["Coin"]
    url = "https://api.nomics.com/v1/currencies/sparkline?key=2baa6243a49438a70af105695e3e951f&ids=" + coinName + "&start=" + timeStart + "&end=" + timeEnd + "&convert=CAD"
    time.sleep(1)
    return json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

def getPricesDay(day, coins): #For All transactions for a singe day, takes 1 sec per check
    
    timestamp = day+"T00%3A00%3A00Z"
    coinList = ""
    for coin in coins:
        coinList += coin + ","
    url = "https://api.nomics.com/v1/currencies/sparkline?key=2baa6243a49438a70af105695e3e951f&ids=" + coinList[0:-1] + "&start=" + timestamp + "&end=" + timestamp + "&convert=CAD"
    output = {}
    time.sleep(1)
    for coin in json.loads(urllib.request.urlopen(url).read().decode("utf-8")):
        output[coin["currency"]] = coin["prices"][0]
    return output

def splitIntoDays(csvIn, timeStart=0, timeEnd=int(time.time())):

    output = {}

    for row in csvIn:
        if timeStart > int(row["Timestamp"]) or timeEnd < int(row["Timestamp"]):
            continue
        date = row["Date"][0:10]
        if not date in output:
            output[date] = {}
        if not row["Coin"] in output[date]:
            output[date][row["Coin"]] = []
        output[date][row["Coin"]].append(row)
        #output[date][row["Coin"]].append(float(row["AmountCoin"]))
    return output
        
def splitIntoCoins(csvIn, timeStart=0, timeEnd=int(time.time())):
    output = {}

    for row in csvIn:
        if timeStart > int(row["Timestamp"]):
            continue
        if timeEnd < int(row["Timestamp"]):
            break
        coin = row["Coin"]
        if not coin in output:
            output[coin] = []
        output[coin].append(row)
        #output[date][row["Coin"]].append(float(row["AmountCoin"]))
    return output

#makeCoinBaseCSV() #Do Not Call, requires manual edits of transactions based on incomes and purchases
#makeCoinBaseProCSV()
#makeBinanceCSVFromTotalStatement() #Requires the CSV that is downloaded to be edited for the transactions sent to binance for purchases or just transactions
#makeOKExCSV() #Requires the transactions to be manually made
#combineAndSortCSV()
#getHistory(JSONOut="Wallet2020.json",timestampEnd=1609459200)
getHistory() #Must Manually change CGLD to CELO and HNT to HELIUM and ALICE to ALICE2 and TLM to TLM2 and TKO to TKO2