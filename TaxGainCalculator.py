import CoinCollector

portfolio = {"totalBal": 0, "totalValue": 0, "totalGain": 0, "totalIn": 0, "LatestTime": {}}

CoinCollector.getCoinBaseCoins(portfolio)

print("Current TotalBal:\t" + str(round(portfolio["totalBal"],8)))
print("Current TotalValue:\t" + str(round(portfolio["totalValue"],8)))
print("Current TotalGain:\t" + str(round(portfolio["totalGain"],8)))
print("Current TotalIn:\t" + str(round(portfolio["totalIn"],8)))
print("TotalGain + TotalIn\t" + str(round(portfolio["totalIn"]-portfolio["totalGain"], 8)))

"""
for line in portfolio:
    print(str(line) + ": " + str(portfolio[line]))
"""