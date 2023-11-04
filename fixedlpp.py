import requests, json, time, pyotp, random, base64


with open("config.json") as jsonfile:
    config = json.load(jsonfile)
    cookie1 = config["Auth"]["cookieOne"]
    cookieOne2Step = config["Auth"]["cookieOne2Step"]

    cookie2 = config["Auth"]["cookieTwo"]
    cookieTwo2Step = config["Auth"]["cookieTwo2Step"]

    sellPrie = config["Details"]["sellPrice"]
    itemID = config["Details"]["itemID"]
    
cookies = [cookie1, cookie2]
getProductID = requests.get(f"https://economy.roblox.com/v2/assets/{itemID}/details", cookies = {".ROBLOSECURITY": random.choice(cookies)}).json()["ProductId"]

swap = False

while True:
    if swap == False: 
        swap = True
        cookie = cookie1
        secondCookie = cookie2
        twostepToken = cookieOne2Step
    elif swap == True:
        swap = False
        cookie = cookie2
        secondCookie = cookie1
        twostepToken = cookieTwo2Step
        
    userID = requests.get("https://users.roblox.com/v1/users/authenticated", cookies = {".ROBLOSECURITY": cookie}).json()["id"]
    userID2 = requests.get("https://users.roblox.com/v1/users/authenticated", cookies = {".ROBLOSECURITY": secondCookie}).json()["id"]
    robux = requests.get(f"https://economy.roblox.com/v1/users/{userID2}/currency", cookies = {".ROBLOSECURITY": secondCookie}).json()["robux"]
    if robux == 0:
        print("you have 0 robux")
        time.sleep(999999)
        break
    inv = requests.get(f"https://inventory.roblox.com/v1/users/{userID}/assets/collectibles?cursor=&limit=100&sortOrder=Desc", cookies = {".ROBLOSECURITY": cookie}).json()["data"]
    
    for item in inv:
        if item["assetId"] == itemID:
            uaid = item["userAssetId"]
            Buypayload = {"expectedCurrency": 1, "expectedPrice": sellPrie, "expectedSellerId": userID, "userAssetId": uaid}

            xcsrf1 = requests.post("https://auth.roblox.com/v2/login", cookies = {".ROBLOSECURITY": cookie}).headers['X-CSRF-TOKEN']
            xcsrf2 = requests.post("https://auth.roblox.com/v2/login", cookies = {".ROBLOSECURITY": secondCookie}).headers['X-CSRF-TOKEN']

            sell = requests.patch(f"https://economy.roblox.com/v1/assets/{itemID}/resellable-copies/{uaid}", json={"price":sellPrie}, headers = {"X-CSRF-TOKEN": xcsrf1}, cookies = {".ROBLOSECURITY": cookie})
            buy = requests.post(f"https://economy.roblox.com/v1/purchases/products/{getProductID}?1",json=Buypayload, headers = {"X-CSRF-TOKEN": xcsrf2}, cookies = {".ROBLOSECURITY": secondCookie})

            print(sell.json())
            print(buy.json())

            time.sleep(10)

            if sell.json() == {'errors': [{'code': 0, 'message': 'Challenge is required to authorize the request'}]}:
                RblxChallengeId = sell.headers["Rblx-Challenge-Id"]
                RblxChallengeMetadata = sell.headers["Rblx-Challenge-Metadata"]
                DecodedRblxChallengeMetadata = json.loads(base64.b64decode(RblxChallengeMetadata).decode('utf-8'))
                EncodedRblxChallengeId = DecodedRblxChallengeMetadata["challengeId"]

                stageOne = requests.post(f"https://twostepverification.roblox.com/v1/users/{userID}/challenges/authenticator/verify", json = {"challengeId":DecodedRblxChallengeMetadata["challengeId"],"actionType":"Generic","code":pyotp.TOTP(twostepToken).now()}, headers = {"X-CSRF-TOKEN": xcsrf1}, cookies = {".ROBLOSECURITY": cookie})
                verificationToken = stageOne.json()["verificationToken"]

                rawMetaData = {"verificationToken": verificationToken, "rememberDevice": False, "challengeId": EncodedRblxChallengeId, "actionType": "Generic"}
                rawMetaDataJson = json.dumps(rawMetaData)
                rawMetaDataJson = rawMetaDataJson.replace(" ", "")
                encodedRblxChallengeMetadata = base64.b64encode(rawMetaDataJson.encode('utf-8')).decode('utf-8')

                sell = requests.patch(f"https://economy.roblox.com/v1/assets/{itemID}/resellable-copies/{uaid}", json={"price":sellPrie}, headers = {"X-CSRF-TOKEN": xcsrf1, "Rblx-Challenge-Id": RblxChallengeId, "Rblx-Challenge-Metadata": encodedRblxChallengeMetadata, "Rblx-Challenge-Type": "twostepverification"}, cookies = {".ROBLOSECURITY": cookie})
                buy = requests.post(f"https://economy.roblox.com/v1/purchases/products/{getProductID}?1",json=Buypayload, headers = {"X-CSRF-TOKEN": xcsrf2}, cookies = {".ROBLOSECURITY": secondCookie})
                
                print(sell.json())
                print(buy.json())

                time.sleep(10)
            swap = True
            break