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

def create_accounts(
    name :str, 
    email : str, 
    dob : str,
    taxId : str, 
    taxCountry : str,
    street : str,
    postalCode : str,
    city : str,
    region: str,
    country: str
):
    path = f"{BASE_URL}/v2/accounts"

    payload = {
        "data": {
            "type": "accounts",
            "attributes": {
                "name": name + "'s Account",
                "authorized-signature": name,
                "account-type": "custodial",
                "owner" : {
                    "contact-type" : "natural_person",
                    "name" : name,
                    "email" : email,
                    "date-of-birth" : dob,
                    "tax-id-number" : taxId,
                    "tax-country" : taxCountry,
                    "primary-phone-number" : {
                        "country" : "US",
                        "number" : "1234567890",
                        "sms" : False
                    },
                    "primary-address" : {
                        "street-1" : street,
                        "street-2" : "",
                        "postal-code" : postalCode,
                        "city" : city,
                        "region" : region,
                        "country" : country
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