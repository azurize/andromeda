from dotenv import load_dotenv
from flask import session
from pymongo import MongoClient

import json
import os
import requests

load_dotenv()

client = MongoClient(os.environ.get('MONGODB_URI'))
db = client.andromeda
users = db.users
dbEmail = db.users.find_one({'email' : session.get('email')})

ENV = os.environ.get('ENV')
BASE_URL = f"https://{ENV}.primetrust.com"
HEADERS = {"Authorization": "Bearer " + os.environ.get('TOKEN')}

def create_accounts(**kwargs):
    path = f"{BASE_URL}/v2/accounts"

    payload = {
        "data": {
            "type": "accounts",
            "attributes": {
                "name": kwargs["name"] + "'s Account",
                "authorized-signature": kwargs["name"],
                "account-type": "custodial",
                "owner" : {
                    "contact-type" : "natural_person",
                    "name" : kwargs["name"],
                    "email" : kwargs["email"],
                    "date-of-birth" : kwargs["dob"],
                    "tax-id-number" : kwargs["taxId"],
                    "tax-country" : kwargs["taxCountry"],
                    "primary-phone-number" : {
                        "country" : "US",
                        "number" : "1234567890",
                        "sms" : False
                    },
                    "primary-address" : {
                        "street-1" : kwargs["street"],
                        "street-2" : "",
                        "postal-code" : kwargs["postalCode"],
                        "city" : kwargs["city"],
                        "region" : kwargs["region"],
                        "country" : kwargs["countr"]
                    }
                }
            }
        }
    }

    response = requests.post(path, headers=HEADERS, json=payload).json()
    output = response.json()["data"]["id"]
    db.users.update_one(
        {'email' : dbEmail}, {'$set' : {'accountId' : output}}
    )

def get_account_totals(account_id : str):
    account_id = db.users.find_one({'email' : 0, 'accountId' : 1})

    path = f"{BASE_URL}/v2/account-cash-totals?account.id={account_id}"

    response = requests.get(path, headers=HEADERS).json()