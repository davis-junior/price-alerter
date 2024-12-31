import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WEB_DRIVER_PORT = 4444
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

DB_FILE_NAME = "price_alerter.db"

PRODUCTS = [
    # Phones
    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.amazon.com/SAMSUNG-Smartphone-Unlocked-Processor-SM-S921UZKAXAA/dp/B0CMDRCZBJ?crid=3TGR10222RZQ5&dib=eyJ2IjoiMSJ9.y9JFwPsCZ9T11Z3y5qhMBtRMll8jhQlxP_N-PHhBkFEwkZRpqsxsXsELKj5t4TZ4RDCDPFvsPDINtShkeCC55KHdCxqCaT1_yA7y1JA3Kv47g6u30i2wWq7zyCS70hdxLRKth2JwtbIINpHORPqqe57O8WVTk9dokRXvmEBgdhXHuknB8TgPLhjv19BPN8C7S5mHXupTmfIju5up-RSTHdnHKduTNuzkhgUKGA3yhMQ.ZweycM1UvriqOnzi2ruEPCOdOh0nSx2x1MNMr4zFeRU&dib_tag=se&keywords=galaxy+s24&qid=1732848837&sprefix=galaxy+s24%2Caps%2C132&sr=8-3",
        "target_price": 400,
    },
    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.bestbuy.com/site/samsung-galaxy-s24-128gb-unlocked-onyx-black/6569840.p?skuId=6569840",
        "target_price": 400,
    },
    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.walmart.com/ip/SAMSUNG-Galaxy-S24-Cell-Phone-128GB-AI-Smartphone-Unlocked-Android-50MP-Camera-Fastest-Processor-Long-Battery-Life-US-Version-2024-Onyx-Black/5400713211?classType=REGULAR&from=/search",
        "target_price": 400,
    },
    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.samsung.com/us/smartphones/galaxy-s24/buy/galaxy-s24-128gb-unlocked-sm-s921ulbaxaa/",
        "target_price": 400,
    },
    # Mowers
    {
        "name": 'Hart 20" Push Mower (not self-propelled)',
        "url": "https://www.walmart.com/ip/HART-40-Volt-20-inch-Cordless-Brushless-Push-Mower-Kit-1-6-0Ah-Lithium-Ion-Battery/990402225?classType=VARIANT&from=/search",
        "target_price": 250,
    },
    {
        "name": 'Hart 20" Push Mower (self-propelled)',
        "url": "https://www.walmart.com/ip/HART-40-Volt-20-inch-Self-Propelled-Battery-Powered-Brushless-Mower-Kit-1-6-0Ah-Lithium-Ion-Battery/399430920?classType=VARIANT&athbdg=L1600&from=/search",
        "target_price": 300,
    },
    {
        "name": 'Hart 20" Push Mower (not self-propelled)',
        "url": "https://harttools.com/products/40v-20-push-mower-kit",
        "target_price": 250,
    },
    {
        "name": 'Hart 20" Push Mower (self-propelled)',
        "url": "https://harttools.com/products/40v-brushless-20-self-propelled-mower",
        "target_price": 300,
    },
    # Home products
    {
        "name": "Hugger 56 in. LED Espresso Bronze Ceiling Fan",
        "url": "https://www.homedepot.com/p/Hugger-56-in-LED-Espresso-Bronze-Ceiling-Fan-AL383D-EB/304542818",
        "target_price": 46,
    },
    {
        "name": "Hugger 52 in. LED Gunmetal Ceiling Fan",
        "url": "https://www.homedepot.com/p/Hugger-52-in-LED-Gunmetal-Ceiling-Fan-AL383LED-GM/304542817",
        "target_price": 45,
    },
    {
        "name": "Trice 52 in. LED Espresso Bronze Ceiling Fan",
        "url": "https://www.homedepot.com/p/Trice-52-in-LED-Espresso-Bronze-Ceiling-Fan-YG269BP-EB/304542645?MERCH=REC-_-brand_based_collection-_-304542817-_-4-_-n/a-_-n/a-_-n/a-_-n/a-_-n/a",
        "target_price": 45,
    },
    # Instruments
    {
        "name": "Alesis Nitro Max Electric Drum Set",
        "url": "https://www.amazon.com/Alesis-Electric-Bluetooth-Authentic-Sounds/dp/B0C43R8SRB/",
        "target_price": 310,
    },
    {
        "name": "Alesis Nitro Pro Electric Drum Set",
        "url": "https://www.amazon.com/Alesis-Electric-Bluetooth-Authentic-Sounds/dp/B0DB5TMZ9S/",
        "target_price": 420,
    },
    {
        "name": "Alesis Nitro Max Electric Drum Set",
        "url": "https://www.musiciansfriend.com/drums-percussion/alesis-nitro-max-8-piece-electronic-drum-set-with-bluetooth-and-bfd-sounds/m06882000001000",
        "target_price": 310,
    },
    {
        "name": "Alesis Nitro Pro Electric Drum Set",
        "url": "https://www.musiciansfriend.com/drums-percussion/alesis-nitro-pro-8-piece-pro-electronic-drum-kit-with-mesh-heads-bluetooth/m14632000000000?rNtt=alesis%20nitro%20pro&index=2",
        "target_price": 420,
    },
    {
        "name": "Alesis Nitro Max Electric Drum Set",
        "url": "https://www.guitarcenter.com/Alesis/Nitro-MAX-8-Piece-Electronic-Drum-Set-With-Bluetooth-and-BFD-Sounds-Black-1500000413581.gc",
        "target_price": 310,
    },
    {
        "name": "Alesis Nitro Pro Electric Drum Set",
        "url": "https://www.guitarcenter.com/Alesis/Nitro-Pro-8-Piece-Pro-Electronic-Drum-Kit-With-Mesh-Heads-Bluetooth-1500000437603.gc",
        "target_price": 420,
    },
]
