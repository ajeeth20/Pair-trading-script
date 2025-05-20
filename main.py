# main.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import requests
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_KEY = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
with open('/tmp/service-account.json', 'w') as f:
    f.write(SERVICE_ACCOUNT_KEY)
credentials = service_account.Credentials.from_service_account_file(
    '/tmp/service-account.json', scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# API credentials for Dhan
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "access-token": os.environ.get('DHAN_ACCESS_TOKEN'),
    "client-id": os.environ.get('DHAN_CLIENT_ID')
}

# Define stock pairs
stock_pairs = [
    {
        "stock1": {
            "security_id": "2303",
            "name": "HAL",
            "column": "HAL_Close",
            "sector": "Aerospace & Defense",
        },
        "stock2": {
            "security_id": "383",
            "name": "BEL",
            "column": "BEL_Close",
            "sector": "Aerospace & Defense",
        },
    },
    {
        "stock1": {
            "security_id": "24184",
            "name": "PIIND",
            "column": "PIIND_Close",
            "sector": "Agrochemicals",
        },
        "stock2": {
            "security_id": "11287",
            "name": "UPL",
            "column": "UPL_Close",
            "sector": "Agrochemicals",
        },
    },
    {
        "stock1": {
            "security_id": "25510",
            "name": "MOTHERSON",
            "column": "MOTHERSON_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "2181",
            "name": "BOSCHLTD",
            "column": "BOSCHLTD_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "25510",
            "name": "MOTHERSON",
            "column": "MOTHERSON_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "312",
            "name": "TIINDIA",
            "column": "TIINDIA_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "25510",
            "name": "MOTHERSON",
            "column": "MOTHERSON_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "422",
            "name": "BHARATFORG",
            "column": "BHARATFORG_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "25510",
            "name": "MOTHERSON",
            "column": "MOTHERSON_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "4684",
            "name": "SONACOMS",
            "column": "SONACOMS_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "2181",
            "name": "BOSCHLTD",
            "column": "BOSCHLTD_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "312",
            "name": "TIINDIA",
            "column": "TIINDIA_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "2181",
            "name": "BOSCHLTD",
            "column": "BOSCHLTD_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "422",
            "name": "BHARATFORG",
            "column": "BHARATFORG_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "2181",
            "name": "BOSCHLTD",
            "column": "BOSCHLTD_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "4684",
            "name": "SONACOMS",
            "column": "SONACOMS_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "312",
            "name": "TIINDIA",
            "column": "TIINDIA_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "422",
            "name": "BHARATFORG",
            "column": "BHARATFORG_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "312",
            "name": "TIINDIA",
            "column": "TIINDIA_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "4684",
            "name": "SONACOMS",
            "column": "SONACOMS_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "422",
            "name": "BHARATFORG",
            "column": "BHARATFORG_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "4684",
            "name": "SONACOMS",
            "column": "SONACOMS_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "25510",
            "name": "MOTHERSON",
            "column": "MOTHERSON_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "676",
            "name": "EXIDEIND",
            "column": "EXIDEIND_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "2181",
            "name": "BOSCHLTD",
            "column": "BOSCHLTD_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "676",
            "name": "EXIDEIND",
            "column": "EXIDEIND_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "312",
            "name": "TIINDIA",
            "column": "TIINDIA_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "676",
            "name": "EXIDEIND",
            "column": "EXIDEIND_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "422",
            "name": "BHARATFORG",
            "column": "BHARATFORG_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "676",
            "name": "EXIDEIND",
            "column": "EXIDEIND_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "4684",
            "name": "SONACOMS",
            "column": "SONACOMS_Close",
            "sector": "Auto Ancillaries",
        },
        "stock2": {
            "security_id": "676",
            "name": "EXIDEIND",
            "column": "EXIDEIND_Close",
            "sector": "Auto Ancillaries",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
    },

    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "10999",
            "name": "MARUTI",
            "column": "MARUTI_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "2031",
            "name": "M&M",
            "column": "M&M_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "3456",
            "name": "TATAMOTORS",
            "column": "TATAMOTORS_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "16669",
            "name": "BAJAJ-AUTO",
            "column": "BAJAJ-AUTO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "910",
            "name": "EICHERMOT",
            "column": "EICHERMOT_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "8479",
            "name": "TVSMOTOR",
            "column": "TVSMOTOR_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "1348",
            "name": "HEROMOTOCO",
            "column": "HEROMOTOCO_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "212",
            "name": "ASHOKLEY",
            "column": "ASHOKLEY_Close",
            "sector": "Automobiles",
        },
        "stock2": {
            "security_id": "958",
            "name": "ESCORTS",
            "column": "ESCORTS_Close",
            "sector": "Automobiles",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1333",
            "name": "HDFCBANK",
            "column": "HDFCBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4963",
            "name": "ICICIBANK",
            "column": "ICICIBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "3045",
            "name": "SBIN",
            "column": "SBIN_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "1922",
            "name": "KOTAKBANK",
            "column": "KOTAKBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5900",
            "name": "AXISBANK",
            "column": "AXISBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4668",
            "name": "BANKBARODA",
            "column": "BANKBARODA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10666",
            "name": "PNB",
            "column": "PNB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10753",
            "name": "UNIONBANK",
            "column": "UNIONBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "10794",
            "name": "CANBK",
            "column": "CANBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "14309",
            "name": "INDIANB",
            "column": "INDIANB_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "11915",
            "name": "YESBANK",
            "column": "YESBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "5258",
            "name": "INDUSINDBK",
            "column": "INDUSINDBK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "21238",
            "name": "AUBANK",
            "column": "AUBANK_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "11184",
            "name": "IDFCFIRSTB",
            "column": "IDFCFIRSTB_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "1023",
            "name": "FEDERALBNK",
            "column": "FEDERALBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "2263",
            "name": "BANDHANBNK",
            "column": "BANDHANBNK_Close",
            "sector": "Banking",
        },
    },
    {
        "stock1": {
            "security_id": "4745",
            "name": "BANKINDIA",
            "column": "BANKINDIA_Close",
            "sector": "Banking",
        },
        "stock2": {
            "security_id": "18391",
            "name": "RBLBANK",
            "column": "RBLBANK_Close",
            "sector": "Banking",
        },
    },
    {'stock1': {'security_id': '11184', 'name': 'IDFCFIRSTB', 'column': 'IDFCFIRSTB_Close', 'sector': 'Banking'}, 'stock2': {'security_id': '1023', 'name': 'FEDERALBNK', 'column': 'FEDERALBNK_Close', 'sector': 'Banking'}},
    {'stock1': {'security_id': '11184', 'name': 'IDFCFIRSTB', 'column': 'IDFCFIRSTB_Close', 'sector': 'Banking'}, 'stock2': {'security_id': '2263', 'name': 'BANDHANBNK', 'column': 'BANDHANBNK_Close', 'sector': 'Banking'}},
    {'stock1': {'security_id': '11184', 'name': 'IDFCFIRSTB', 'column': 'IDFCFIRSTB_Close', 'sector': 'Banking'}, 'stock2': {'security_id': '18391', 'name': 'RBLBANK', 'column': 'RBLBANK_Close', 'sector': 'Banking'}},
    {'stock1': {'security_id': '1023', 'name': 'FEDERALBNK', 'column': 'FEDERALBNK_Close', 'sector': 'Banking'}, 'stock2': {'security_id': '2263', 'name': 'BANDHANBNK', 'column': 'BANDHANBNK_Close', 'sector': 'Banking'}},
    {'stock1': {'security_id': '1023', 'name': 'FEDERALBNK', 'column': 'FEDERALBNK_Close', 'sector': 'Banking'}, 'stock2': {'security_id': '18391', 'name': 'RBLBANK', 'column': 'RBLBANK_Close', 'sector': 'Banking'}},
    {'stock1': {'security_id': '2263', 'name': 'BANDHANBNK', 'column': 'BANDHANBNK_Close', 'sector': 'Banking'}, 'stock2': {'security_id': '18391', 'name': 'RBLBANK', 'column': 'RBLBANK_Close', 'sector': 'Banking'}},
    {'stock1': {'security_id': '10447', 'name': 'UNITDSPR', 'column': 'UNITDSPR_Close', 'sector': 'Beverages'}, 'stock2': {'security_id': '16713', 'name': 'UBL', 'column': 'UBL_Close', 'sector': 'Beverages'}},
    {'stock1': {'security_id': '10447', 'name': 'UNITDSPR', 'column': 'UNITDSPR_Close', 'sector': 'Beverages'}, 'stock2': {'security_id': '18921', 'name': 'VBL', 'column': 'VBL_Close', 'sector': 'Beverages'}},
    {'stock1': {'security_id': '16713', 'name': 'UBL', 'column': 'UBL_Close', 'sector': 'Beverages'}, 'stock2': {'security_id': '18921', 'name': 'VBL', 'column': 'VBL_Close', 'sector': 'Beverages'}},
    {'stock1': {'security_id': '11373', 'name': 'BIOCON', 'column': 'BIOCON_Close', 'sector': 'Biotechnology'}, 'stock2': {'security_id': '10243', 'name': 'SYNGENE', 'column': 'SYNGENE_Close', 'sector': 'Biotechnology'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '11532', 'name': 'ULTRACEMCO', 'column': 'ULTRACEMCO_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '1270', 'name': 'AMBUJACEM', 'column': 'AMBUJACEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '3103', 'name': 'SHREECEM', 'column': 'SHREECEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '13270', 'name': 'JKCEMENT', 'column': 'JKCEMENT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '8075', 'name': 'DALBHARAT', 'column': 'DALBHARAT_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '22', 'name': 'ACC', 'column': 'ACC_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '2043', 'name': 'RAMCOCEM', 'column': 'RAMCOCEM_Close', 'sector': 'Cement'}, 'stock2': {'security_id': '1515', 'name': 'INDIACEM', 'column': 'INDIACEM_Close', 'sector': 'Cement'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2664', 'name': 'PIDILITIND', 'column': 'PIDILITIND_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '13332', 'name': 'SOLARINDS', 'column': 'SOLARINDS_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3273', 'name': 'SRF', 'column': 'SRF_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '19943', 'name': 'DEEPAKNTR', 'column': 'DEEPAKNTR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '14672', 'name': 'NAVINFLUOR', 'column': 'NAVINFLUOR_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '3405', 'name': 'TATACHEM', 'column': 'TATACHEM_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '263', 'name': 'ATUL', 'column': 'ATUL_Close', 'sector': 'Chemicals'}, 'stock2': {'security_id': '7', 'name': 'AARTIIND', 'column': 'AARTIIND_Close', 'sector': 'Chemicals'}},
    {'stock1': {'security_id': '2885', 'name': 'RELIANCE', 'column': 'RELIANCE_Close', 'sector': 'Conglomerate'}, 'stock2': {'security_id': '25', 'name': 'ADANIENT', 'column': 'ADANIENT_Close', 'sector': 'Conglomerate'}},
    {'stock1': {'security_id': '2885', 'name': 'RELIANCE', 'column': 'RELIANCE_Close', 'sector': 'Conglomerate'}, 'stock2': {'security_id': '1232', 'name': 'GRASIM', 'column': 'GRASIM_Close', 'sector': 'Conglomerate'}},
    {'stock1': {'security_id': '25', 'name': 'ADANIENT', 'column': 'ADANIENT_Close', 'sector': 'Conglomerate'}, 'stock2': {'security_id': '1232', 'name': 'GRASIM', 'column': 'GRASIM_Close', 'sector': 'Conglomerate'}},
    {'stock1': {'security_id': '3718', 'name': 'VOLTAS', 'column': 'VOLTAS_Close', 'sector': 'Consumer Durables / Electrical'}, 'stock2': {'security_id': '17094', 'name': 'CROMPTON', 'column': 'CROMPTON_Close', 'sector': 'Consumer Durables / Electrical'}},
    {'stock1': {'security_id': '3506', 'name': 'TITAN', 'column': 'TITAN_Close', 'sector': 'Consumer Durables / Jewellery'}, 'stock2': {'security_id': '2955', 'name': 'KALYANKJIL', 'column': 'KALYANKJIL_Close', 'sector': 'Consumer Durables / Jewellery'}},
    {'stock1': {'security_id': '6545', 'name': 'NYKAA', 'column': 'NYKAA_Close', 'sector': 'E-Commerce'}, 'stock2': {'security_id': '10726', 'name': 'INDIAMART', 'column': 'INDIAMART_Close', 'sector': 'E-Commerce'}},
    {'stock1': {'security_id': '13', 'name': 'ABB', 'column': 'ABB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '3150', 'name': 'SIEMENS', 'column': 'SIEMENS_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '13', 'name': 'ABB', 'column': 'ABB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '9819', 'name': 'HAVELLS', 'column': 'HAVELLS_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '13', 'name': 'ABB', 'column': 'ABB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '760', 'name': 'CGPOWER', 'column': 'CGPOWER_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '13', 'name': 'ABB', 'column': 'ABB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '9590', 'name': 'POLYCAB', 'column': 'POLYCAB_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '13', 'name': 'ABB', 'column': 'ABB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '438', 'name': 'BHEL', 'column': 'BHEL_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '13', 'name': 'ABB', 'column': 'ABB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '13310', 'name': 'KEI', 'column': 'KEI_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '3150', 'name': 'SIEMENS', 'column': 'SIEMENS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '9819', 'name': 'HAVELLS', 'column': 'HAVELLS_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '3150', 'name': 'SIEMENS', 'column': 'SIEMENS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '760', 'name': 'CGPOWER', 'column': 'CGPOWER_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '3150', 'name': 'SIEMENS', 'column': 'SIEMENS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '9590', 'name': 'POLYCAB', 'column': 'POLYCAB_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '3150', 'name': 'SIEMENS', 'column': 'SIEMENS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '438', 'name': 'BHEL', 'column': 'BHEL_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '3150', 'name': 'SIEMENS', 'column': 'SIEMENS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '13310', 'name': 'KEI', 'column': 'KEI_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '9819', 'name': 'HAVELLS', 'column': 'HAVELLS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '760', 'name': 'CGPOWER', 'column': 'CGPOWER_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '9819', 'name': 'HAVELLS', 'column': 'HAVELLS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '9590', 'name': 'POLYCAB', 'column': 'POLYCAB_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '9819', 'name': 'HAVELLS', 'column': 'HAVELLS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '438', 'name': 'BHEL', 'column': 'BHEL_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '9819', 'name': 'HAVELLS', 'column': 'HAVELLS_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '13310', 'name': 'KEI', 'column': 'KEI_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '760', 'name': 'CGPOWER', 'column': 'CGPOWER_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '9590', 'name': 'POLYCAB', 'column': 'POLYCAB_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '760', 'name': 'CGPOWER', 'column': 'CGPOWER_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '438', 'name': 'BHEL', 'column': 'BHEL_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '760', 'name': 'CGPOWER', 'column': 'CGPOWER_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '13310', 'name': 'KEI', 'column': 'KEI_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '9590', 'name': 'POLYCAB', 'column': 'POLYCAB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '438', 'name': 'BHEL', 'column': 'BHEL_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '9590', 'name': 'POLYCAB', 'column': 'POLYCAB_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '13310', 'name': 'KEI', 'column': 'KEI_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '438', 'name': 'BHEL', 'column': 'BHEL_Close', 'sector': 'Electrical Equipment'}, 'stock2': {'security_id': '13310', 'name': 'KEI', 'column': 'KEI_Close', 'sector': 'Electrical Equipment'}},
    {'stock1': {'security_id': '19585', 'name': 'BSE', 'column': 'BSE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '31181', 'name': 'MCX', 'column': 'MCX_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '19585', 'name': 'BSE', 'column': 'BSE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '21174', 'name': 'CDSL', 'column': 'CDSL_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '19585', 'name': 'BSE', 'column': 'BSE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '324', 'name': 'ANGELONE', 'column': 'ANGELONE_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '19585', 'name': 'BSE', 'column': 'BSE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '342', 'name': 'CAMS', 'column': 'CAMS_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '19585', 'name': 'BSE', 'column': 'BSE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '220', 'name': 'IEX', 'column': 'IEX_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '31181', 'name': 'MCX', 'column': 'MCX_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '21174', 'name': 'CDSL', 'column': 'CDSL_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '31181', 'name': 'MCX', 'column': 'MCX_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '324', 'name': 'ANGELONE', 'column': 'ANGELONE_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '31181', 'name': 'MCX', 'column': 'MCX_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '342', 'name': 'CAMS', 'column': 'CAMS_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '31181', 'name': 'MCX', 'column': 'MCX_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '220', 'name': 'IEX', 'column': 'IEX_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '21174', 'name': 'CDSL', 'column': 'CDSL_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '324', 'name': 'ANGELONE', 'column': 'ANGELONE_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '21174', 'name': 'CDSL', 'column': 'CDSL_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '342', 'name': 'CAMS', 'column': 'CAMS_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '21174', 'name': 'CDSL', 'column': 'CDSL_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '220', 'name': 'IEX', 'column': 'IEX_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '324', 'name': 'ANGELONE', 'column': 'ANGELONE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '342', 'name': 'CAMS', 'column': 'CAMS_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '324', 'name': 'ANGELONE', 'column': 'ANGELONE_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '220', 'name': 'IEX', 'column': 'IEX_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '342', 'name': 'CAMS', 'column': 'CAMS_Close', 'sector': 'Financial Services'}, 'stock2': {'security_id': '220', 'name': 'IEX', 'column': 'IEX_Close', 'sector': 'Financial Services'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1394', 'name': 'HINDUNILVR', 'column': 'HINDUNILVR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '1660', 'name': 'ITC', 'column': 'ITC_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '17963', 'name': 'NESTLEIND', 'column': 'NESTLEIND_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '547', 'name': 'BRITANNIA', 'column': 'BRITANNIA_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '10099', 'name': 'GODREJCP', 'column': 'GODREJCP_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '3432', 'name': 'TATACONSUM', 'column': 'TATACONSUM_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '4067', 'name': 'MARICO', 'column': 'MARICO_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '772', 'name': 'DABUR', 'column': 'DABUR_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '15141', 'name': 'COLPAL', 'column': 'COLPAL_Close', 'sector': 'FMCG'}, 'stock2': {'security_id': '17029', 'name': 'PATANJALI', 'column': 'PATANJALI_Close', 'sector': 'FMCG'}},
    {'stock1': {'security_id': '22377', 'name': 'MAXHEALTH', 'column': 'MAXHEALTH_Close', 'sector': 'Healthcare'}, 'stock2': {'security_id': '157', 'name': 'APOLLOHOSP', 'column': 'APOLLOHOSP_Close', 'sector': 'Healthcare'}},
    {'stock1': {'security_id': '22377', 'name': 'MAXHEALTH', 'column': 'MAXHEALTH_Close', 'sector': 'Healthcare'}, 'stock2': {'security_id': '11654', 'name': 'LALPATHLAB', 'column': 'LALPATHLAB_Close', 'sector': 'Healthcare'}},
    {'stock1': {'security_id': '22377', 'name': 'MAXHEALTH', 'column': 'MAXHEALTH_Close', 'sector': 'Healthcare'}, 'stock2': {'security_id': '9581', 'name': 'METROPOLIS', 'column': 'METROPOLIS_Close', 'sector': 'Healthcare'}},
    {'stock1': {'security_id': '157', 'name': 'APOLLOHOSP', 'column': 'APOLLOHOSP_Close', 'sector': 'Healthcare'}, 'stock2': {'security_id': '11654', 'name': 'LALPATHLAB', 'column': 'LALPATHLAB_Close', 'sector': 'Healthcare'}},
    {'stock1': {'security_id': '157', 'name': 'APOLLOHOSP', 'column': 'APOLLOHOSP_Close', 'sector': 'Healthcare'}, 'stock2': {'security_id': '9581', 'name': 'METROPOLIS', 'column': 'METROPOLIS_Close', 'sector': 'Healthcare'}},
    {'stock1': {'security_id': '11654', 'name': 'LALPATHLAB', 'column': 'LALPATHLAB_Close', 'sector': 'Healthcare'}, 'stock2': {'security_id': '9581', 'name': 'METROPOLIS', 'column': 'METROPOLIS_Close', 'sector': 'Healthcare'}},
    {'stock1': {'security_id': '11483', 'name': 'LT', 'column': 'LT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '15083', 'name': 'ADANIPORTS', 'column': 'ADANIPORTS_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '11483', 'name': 'LT', 'column': 'LT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '13528', 'name': 'GMRAIRPORT', 'column': 'GMRAIRPORT_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '11483', 'name': 'LT', 'column': 'LT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '15313', 'name': 'IRB', 'column': 'IRB_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '11483', 'name': 'LT', 'column': 'LT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '31415', 'name': 'NBCC', 'column': 'NBCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '11483', 'name': 'LT', 'column': 'LT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '2319', 'name': 'NCC', 'column': 'NCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '15083', 'name': 'ADANIPORTS', 'column': 'ADANIPORTS_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '13528', 'name': 'GMRAIRPORT', 'column': 'GMRAIRPORT_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '15083', 'name': 'ADANIPORTS', 'column': 'ADANIPORTS_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '15313', 'name': 'IRB', 'column': 'IRB_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '15083', 'name': 'ADANIPORTS', 'column': 'ADANIPORTS_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '31415', 'name': 'NBCC', 'column': 'NBCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '15083', 'name': 'ADANIPORTS', 'column': 'ADANIPORTS_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '2319', 'name': 'NCC', 'column': 'NCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '13528', 'name': 'GMRAIRPORT', 'column': 'GMRAIRPORT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '15313', 'name': 'IRB', 'column': 'IRB_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '13528', 'name': 'GMRAIRPORT', 'column': 'GMRAIRPORT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '31415', 'name': 'NBCC', 'column': 'NBCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '13528', 'name': 'GMRAIRPORT', 'column': 'GMRAIRPORT_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '2319', 'name': 'NCC', 'column': 'NCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '15313', 'name': 'IRB', 'column': 'IRB_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '31415', 'name': 'NBCC', 'column': 'NBCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '15313', 'name': 'IRB', 'column': 'IRB_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '2319', 'name': 'NCC', 'column': 'NCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '31415', 'name': 'NBCC', 'column': 'NBCC_Close', 'sector': 'Infrastructure'}, 'stock2': {'security_id': '2319', 'name': 'NCC', 'column': 'NCC_Close', 'sector': 'Infrastructure'}},
    {'stock1': {'security_id': '9480', 'name': 'LICI', 'column': 'LICI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '21808', 'name': 'SBILIFE', 'column': 'SBILIFE_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '9480', 'name': 'LICI', 'column': 'LICI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '467', 'name': 'HDFCLIFE', 'column': 'HDFCLIFE_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '9480', 'name': 'LICI', 'column': 'LICI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '21770', 'name': 'ICICIGI', 'column': 'ICICIGI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '9480', 'name': 'LICI', 'column': 'LICI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '18652', 'name': 'ICICIPRULI', 'column': 'ICICIPRULI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '9480', 'name': 'LICI', 'column': 'LICI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '2142', 'name': 'MFSL', 'column': 'MFSL_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '21808', 'name': 'SBILIFE', 'column': 'SBILIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '467', 'name': 'HDFCLIFE', 'column': 'HDFCLIFE_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '21808', 'name': 'SBILIFE', 'column': 'SBILIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '21770', 'name': 'ICICIGI', 'column': 'ICICIGI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '21808', 'name': 'SBILIFE', 'column': 'SBILIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '18652', 'name': 'ICICIPRULI', 'column': 'ICICIPRULI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '21808', 'name': 'SBILIFE', 'column': 'SBILIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '2142', 'name': 'MFSL', 'column': 'MFSL_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '467', 'name': 'HDFCLIFE', 'column': 'HDFCLIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '21770', 'name': 'ICICIGI', 'column': 'ICICIGI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '467', 'name': 'HDFCLIFE', 'column': 'HDFCLIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '18652', 'name': 'ICICIPRULI', 'column': 'ICICIPRULI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '467', 'name': 'HDFCLIFE', 'column': 'HDFCLIFE_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '2142', 'name': 'MFSL', 'column': 'MFSL_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '21770', 'name': 'ICICIGI', 'column': 'ICICIGI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '18652', 'name': 'ICICIPRULI', 'column': 'ICICIPRULI_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '21770', 'name': 'ICICIGI', 'column': 'ICICIGI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '2142', 'name': 'MFSL', 'column': 'MFSL_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '18652', 'name': 'ICICIPRULI', 'column': 'ICICIPRULI_Close', 'sector': 'Insurance'}, 'stock2': {'security_id': '2142', 'name': 'MFSL', 'column': 'MFSL_Close', 'sector': 'Insurance'}},
    {'stock1': {'security_id': '13751', 'name': 'NAUKRI', 'column': 'NAUKRI_Close', 'sector': 'Internet'}, 'stock2': {'security_id': '6656', 'name': 'POLICYBZR', 'column': 'POLICYBZR_Close', 'sector': 'Internet'}},
    {'stock1': {'security_id': '13751', 'name': 'NAUKRI', 'column': 'NAUKRI_Close', 'sector': 'Internet'}, 'stock2': {'security_id': '6705', 'name': 'PAYTM', 'column': 'PAYTM_Close', 'sector': 'Internet'}},
    {'stock1': {'security_id': '6656', 'name': 'POLICYBZR', 'column': 'POLICYBZR_Close', 'sector': 'Internet'}, 'stock2': {'security_id': '6705', 'name': 'PAYTM', 'column': 'PAYTM_Close', 'sector': 'Internet'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
{'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11536', 'name': 'TCS', 'column': 'TCS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '1594', 'name': 'INFY', 'column': 'INFY_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '7229', 'name': 'HCLTECH', 'column': 'HCLTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3787', 'name': 'WIPRO', 'column': 'WIPRO_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '13538', 'name': 'TECHM', 'column': 'TECHM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '17818', 'name': 'LTIM', 'column': 'LTIM_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18365', 'name': 'PERSISTENT', 'column': 'PERSISTENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '10738', 'name': 'OFSS', 'column': 'OFSS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '11543', 'name': 'COFORGE', 'column': 'COFORGE_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4503', 'name': 'MPHASIS', 'column': 'MPHASIS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '18564', 'name': 'LTTS', 'column': 'LTTS_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '3411', 'name': 'TATAELXSI', 'column': 'TATAELXSI_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '9683', 'name': 'KPITTECH', 'column': 'KPITTECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '20293', 'name': 'TATATECH', 'column': 'TATATECH_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '5748', 'name': 'CYIENT', 'column': 'CYIENT_Close', 'sector': 'IT Services'}, 'stock2': {'security_id': '6994', 'name': 'BSOFT', 'column': 'BSOFT_Close', 'sector': 'IT Services'}},
    {'stock1': {'security_id': '4749', 'name': 'CONCOR', 'column': 'CONCOR_Close', 'sector': 'Logistics'}, 'stock2': {'security_id': '9599', 'name': 'DELHIVERY', 'column': 'DELHIVERY_Close', 'sector': 'Logistics'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '20374', 'name': 'COALINDIA', 'column': 'COALINDIA_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11723', 'name': 'JSWSTEEL', 'column': 'JSWSTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3499', 'name': 'TATASTEEL', 'column': 'TATASTEEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1424', 'name': 'HINDZINC', 'column': 'HINDZINC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '3063', 'name': 'VEDL', 'column': 'VEDL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '1363', 'name': 'HINDALCO', 'column': 'HINDALCO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6733', 'name': 'JINDALSTEL', 'column': 'JINDALSTEL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '15332', 'name': 'NMDC', 'column': 'NMDC_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '11236', 'name': 'JSL', 'column': 'JSL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '2963', 'name': 'SAIL', 'column': 'SAIL_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '25780', 'name': 'APLAPOLLO', 'column': 'APLAPOLLO_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '6364', 'name': 'NATIONALUM', 'column': 'NATIONALUM_Close', 'sector': 'Metals'}, 'stock2': {'security_id': '17939', 'name': 'HINDCOPPER', 'column': 'HINDCOPPER_Close', 'sector': 'Metals'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
    {'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '317', 'name': 'BAJFINANCE', 'column': 'BAJFINANCE_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '16675', 'name': 'BAJAJFINSV', 'column': 'BAJAJFINSV_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18143', 'name': 'JIOFIN', 'column': 'JIOFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2029', 'name': 'IRFC', 'column': 'IRFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '14299', 'name': 'PFC', 'column': 'PFC_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19257', 'name': 'CHOLAFIN', 'column': 'CHOLAFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '4306', 'name': 'SHRIRAMFIN', 'column': 'SHRIRAMFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '15355', 'name': 'RECLTD', 'column': 'RECLTD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '23650', 'name': 'MUTHOOTFIN', 'column': 'MUTHOOTFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '17971', 'name': 'SBICARD', 'column': 'SBICARD_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '21614', 'name': 'ABCAPITAL', 'column': 'ABCAPITAL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20261', 'name': 'IREDA', 'column': 'IREDA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '20825', 'name': 'HUDCO', 'column': 'HUDCO_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '24948', 'name': 'LTF', 'column': 'LTF_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '1997', 'name': 'LICHSGFIN', 'column': 'LICHSGFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '13285', 'name': 'M&MFIN', 'column': 'M&MFIN_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '11403', 'name': 'POONAWALLA', 'column': 'POONAWALLA_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '18908', 'name': 'PNBHOUSING', 'column': 'PNBHOUSING_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2412', 'name': 'PEL', 'column': 'PEL_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '19061', 'name': 'MANAPPURAM', 'column': 'MANAPPURAM_Close', 'sector': 'NBFC'}, 'stock2': {'security_id': '11809', 'name': 'IIFL', 'column': 'IIFL_Close', 'sector': 'NBFC'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '2475', 'name': 'ONGC', 'column': 'ONGC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1624', 'name': 'IOC', 'column': 'IOC_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '526', 'name': 'BPCL', 'column': 'BPCL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '4717', 'name': 'GAIL', 'column': 'GAIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '1406', 'name': 'HINDPETRO', 'column': 'HINDPETRO_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '6066', 'name': 'ATGL', 'column': 'ATGL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '17438', 'name': 'OIL', 'column': 'OIL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '11351', 'name': 'PETRONET', 'column': 'PETRONET_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '10599', 'name': 'GUJGASLTD', 'column': 'GUJGASLTD_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '11262', 'name': 'IGL', 'column': 'IGL_Close', 'sector': 'Oil & Gas'}, 'stock2': {'security_id': '17534', 'name': 'MGL', 'column': 'MGL_Close', 'sector': 'Oil & Gas'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3351', 'name': 'SUNPHARMA', 'column': 'SUNPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10940', 'name': 'DIVISLAB', 'column': 'DIVISLAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '694', 'name': 'CIPLA', 'column': 'CIPLA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3518', 'name': 'TORNTPHARM', 'column': 'TORNTPHARM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '881', 'name': 'DRREDDY', 'column': 'DRREDDY_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '10440', 'name': 'LUPIN', 'column': 'LUPIN_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7929', 'name': 'ZYDUSLIFE', 'column': 'ZYDUSLIFE_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '275', 'name': 'AUROPHARMA', 'column': 'AUROPHARMA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '17903', 'name': 'ABBOTINDIA', 'column': 'ABBOTINDIA_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '11703', 'name': 'ALKEM', 'column': 'ALKEM_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '7406', 'name': 'GLENMARK', 'column': 'GLENMARK_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '1633', 'name': 'IPCALAB', 'column': 'IPCALAB_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '19234', 'name': 'LAURUSLABS', 'column': 'LAURUSLABS_Close', 'sector': 'Pharmaceuticals'}, 'stock2': {'security_id': '11872', 'name': 'GRANULES', 'column': 'GRANULES_Close', 'sector': 'Pharmaceuticals'}},
{'stock1': {'security_id': '3363', 'name': 'SUPREMEIND', 'column': 'SUPREMEIND_Close', 'sector': 'Plastics'}, 'stock2': {'security_id': '14418', 'name': 'ASTRAL', 'column': 'ASTRAL_Close', 'sector': 'Plastics'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17400', 'name': 'NHPC', 'column': 'NHPC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '11630', 'name': 'NTPC', 'column': 'NTPC_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17400', 'name': 'NHPC', 'column': 'NHPC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '14977', 'name': 'POWERGRID', 'column': 'POWERGRID_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17400', 'name': 'NHPC', 'column': 'NHPC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '3426', 'name': 'TATAPOWER', 'column': 'TATAPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17400', 'name': 'NHPC', 'column': 'NHPC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}, 'stock2': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}, 'stock2': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}, 'stock2': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '10217', 'name': 'ADANIENSOL', 'column': 'ADANIENSOL_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}, 'stock2': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}, 'stock2': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '17869', 'name': 'JSWENERGY', 'column': 'JSWENERGY_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '13786', 'name': 'TORNTPOWER', 'column': 'TORNTPOWER_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '18883', 'name': 'SJVN', 'column': 'SJVN_Close', 'sector': 'Power'}, 'stock2': {'security_id': '628', 'name': 'CESC', 'column': 'CESC_Close', 'sector': 'Power'}},
{'stock1': {'security_id': '13611', 'name': 'IRCTC', 'column': 'IRCTC_Close', 'sector': 'Railways'}, 'stock2': {'security_id': '15414', 'name': 'TITAGARH', 'column': 'TITAGARH_Close', 'sector': 'Railways'}},
{'stock1': {'security_id': '14732', 'name': 'DLF', 'column': 'DLF_Close', 'sector': 'Real Estate'}, 'stock2': {'security_id': '3220', 'name': 'LODHA', 'column': 'LODHA_Close', 'sector': 'Real Estate'}},
{'stock1': {'security_id': '14732', 'name': 'DLF', 'column': 'DLF_Close', 'sector': 'Real Estate'}, 'stock2': {'security_id': '17875', 'name': 'GODREJPROP', 'column': 'GODREJPROP_Close', 'sector': 'Real Estate'}},
{'stock1': {'security_id': '14413', 'name': 'PAGEIND', 'column': 'PAGEIND_Close', 'sector': 'Retail'}, 'stock2': {'security_id': '1964', 'name': 'TRENT', 'column': 'TRENT_Close', 'sector': 'Retail'}},
{'stock1': {'security_id': '14413', 'name': 'PAGEIND', 'column': 'PAGEIND_Close', 'sector': 'Retail'}, 'stock2': {'security_id': '30108', 'name': 'ABFRL', 'column': 'ABFRL_Close', 'sector': 'Retail'}},
{'stock1': {'security_id': '10604', 'name': 'BHARTIARTL', 'column': 'BHARTIARTL_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '29135', 'name': 'INDUSTOWER', 'column': 'INDUSTOWER_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '10604', 'name': 'BHARTIARTL', 'column': 'BHARTIARTL_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '14366', 'name': 'IDEA', 'column': 'IDEA_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '10604', 'name': 'BHARTIARTL', 'column': 'BHARTIARTL_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '3721', 'name': 'TATACOMM', 'column': 'TATACOMM_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '10604', 'name': 'BHARTIARTL', 'column': 'BHARTIARTL_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '21951', 'name': 'HFCL', 'column': 'HFCL_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '29135', 'name': 'INDUSTOWER', 'column': 'INDUSTOWER_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '14366', 'name': 'IDEA', 'column': 'IDEA_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '29135', 'name': 'INDUSTOWER', 'column': 'INDUSTOWER_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '3721', 'name': 'TATACOMM', 'column': 'TATACOMM_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '29135', 'name': 'INDUSTOWER', 'column': 'INDUSTOWER_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '21951', 'name': 'HFCL', 'column': 'HFCL_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '14366', 'name': 'IDEA', 'column': 'IDEA_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '3721', 'name': 'TATACOMM', 'column': 'TATACOMM_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '14366', 'name': 'IDEA', 'column': 'IDEA_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '21951', 'name': 'HFCL', 'column': 'HFCL_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '3721', 'name': 'TATACOMM', 'column': 'TATACOMM_Close', 'sector': 'Telecommunications'}, 'stock2': {'security_id': '21951', 'name': 'HFCL', 'column': 'HFCL_Close', 'sector': 'Telecommunications'}},
{'stock1': {'security_id': '2277', 'name': 'MRF', 'column': 'MRF_Close', 'sector': 'Tyres / Auto Ancillaries'}, 'stock2': {'security_id': '335', 'name': 'BALKRISIND', 'column': 'BALKRISIND_Close', 'sector': 'Tyres / Auto Ancillaries'}},
{'stock1': {'security_id': '2277', 'name': 'MRF', 'column': 'MRF_Close', 'sector': 'Tyres / Auto Ancillaries'}, 'stock2': {'security_id': '163', 'name': 'APOLLOTYRE', 'column': 'APOLLOTYRE_Close', 'sector': 'Tyres / Auto Ancillaries'}},
{'stock1': {'security_id': '335', 'name': 'BALKRISIND', 'column': 'BALKRISIND_Close', 'sector': 'Tyres / Auto Ancillaries'}, 'stock2': {'security_id': '163', 'name': 'APOLLOTYRE', 'column': 'APOLLOTYRE_Close', 'sector': 'Tyres / Auto Ancillaries'}},
]

# Function to upload to Google Drive (updated to overwrite existing files)
def upload_to_drive(filename, filepath, folder_id):
    # Search for existing file with the same name in the folder
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    response = drive_service.files().list(q=query, fields='files(id, name)').execute()
    files = response.get('files', [])

    media = MediaFileUpload(filepath, mimetype='application/octet-stream')
    if files:
        # File exists, update it
        file_id = files[0]['id']
        file = drive_service.files().update(fileId=file_id, media_body=media).execute()
        logger.info(f"Updated existing file {filename} in Google Drive with ID: {file.get('id')}")
    else:
        # File doesn't exist, create new
        file_metadata = {'name': filename, 'parents': [folder_id]}
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"Created new file {filename} in Google Drive with ID: {file.get('id')}")

def fetch_ohlc(security_id, stock_name, column_name, exchange_segment="NSE_EQ", instrument_type="EQUITY", days=150):
    url = "https://api.dhan.co/v2/charts/historical"
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=days)
    payload = {
        "securityId": security_id,
        "exchangeSegment": exchange_segment,
        "instrument": instrument_type,
        "expiryCode": 0,
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat()
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("close") or not data.get("timestamp"):
            logger.warning(f"No data returned for {stock_name} (security_id: {security_id})")
            return None
        df = pd.DataFrame({
            "Date": [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in data["timestamp"]],
            column_name: data["close"]
        })
        logger.info(f"Fetched {len(df)} rows for {stock_name} from {df['Date'].min()} to {df['Date'].max()}")
        return df
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error for {stock_name} (security_id: {security_id}): {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for {stock_name} (security_id: {security_id}): {e}")
        return None

def send_email(csv_filepath):
    sender_email = os.environ.get('SENDER_EMAIL')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    subject = "Pair Trading Signals CSV"
    body = "Please find attached the latest pair trading signals."

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    filename = os.path.basename(csv_filepath)
    with open(csv_filepath, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)

    app_password = os.environ.get('EMAIL_APP_PASSWORD')
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)
        server.quit()
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def main():
    save_dir = "/tmp/test_results"
    os.makedirs(save_dir, exist_ok=True)
    folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')

    all_signals = []
    for pair in stock_pairs:
        stock1 = pair["stock1"]
        stock2 = pair["stock2"]
        sector = stock1["sector"]
        logger.info(f"Processing pair: {stock1['name']} - {stock2['name']} ({sector})")

        stock_data = {
            stock1["name"]: fetch_ohlc(stock1["security_id"], stock1["name"], stock1["column"]),
            stock2["name"]: fetch_ohlc(stock2["security_id"], stock2["name"], stock2["column"])
        }

        if any(data is None for data in stock_data.values()):
            logger.warning(f"Skipping pair {stock1['name']} - {stock2['name']} due to missing data")
            continue

        df = stock_data[stock1["name"]].set_index("Date")[[stock1["column"]]].join(
            stock_data[stock2["name"]].set_index("Date")[[stock2["column"]]], how="inner"
        )
        df.index = pd.to_datetime(df.index)
        df = df.dropna()

        if df.empty:
            logger.warning(f"Empty DataFrame for {stock1['name']} - {stock2['name']}")
            continue

        logger.info(df.tail(20).to_string())

        X = sm.add_constant(df[stock1["column"]])
        model = sm.OLS(df[stock2["column"]], X).fit()
        logger.info(model.summary().as_text())

        df["predicted"] = model.predict(X)
        df["residuals"] = df[stock2["column"]] - df["predicted"]

        SSE = np.sum(df["residuals"]**2)
        n, k = len(df), X.shape[1]
        standard_error = np.sqrt(SSE / (n - k))
        logger.info(f"Standard Error: {standard_error}")

        adf_result = adfuller(df["residuals"].dropna())
        adf_p_value = adf_result[1]
        logger.info(f"ADF Statistic: {adf_result[0]}, p-value: {adf_p_value}")

        df["deviation_from_std_error"] = df["residuals"] / standard_error
        df["signal"] = None
        df.loc[df["deviation_from_std_error"] < -1.5, "signal"] = f"BUY {stock2['name']}, SELL {stock1['name']}"
        df.loc[df["deviation_from_std_error"] > 1.5, "signal"] = f"SELL {stock2['name']}, BUY {stock1['name']}"

        plot_df = df[["deviation_from_std_error", "signal"]].copy()
        plot_df["date"] = plot_df.index
        csv_path = f"{save_dir}/data_{stock1['name']}_{stock2['name']}.csv"
        plot_df.to_csv(csv_path, index=False)
        upload_to_drive(f"data_{stock1['name']}_{stock2['name']}.csv", csv_path, folder_id)
        logger.info(f"Saved CSV to {csv_path} and uploaded to Google Drive")

        signal_df = df[df["signal"].notnull()][["deviation_from_std_error", "signal"]].copy()
        signal_df["stock1_name"] = stock1["name"]
        signal_df["stock2_name"] = stock2["name"]
        signal_df["sector"] = sector
        signal_df["date"] = signal_df.index
        signal_df["adf_p_value"] = adf_p_value
        all_signals.append(signal_df.reset_index(drop=True))
        logger.info(signal_df.tail(10).to_string())

        plt.figure(figsize=(14, 6))
        plt.plot(df.index, df["deviation_from_std_error"], label="Deviation from Std Error", color="blue")
        plt.axhline(1.5, color="red", linestyle="--", label="+1.5 Std Error")
        plt.axhline(-1.5, color="green", linestyle="--", label="-1.5 Std Error")
        plt.axhline(0, color="black", linestyle="-")
        plt.scatter(
            df[df["signal"] == f"BUY {stock2['name']}, SELL {stock1['name']}"].index,
            df[df["signal"] == f"BUY {stock2['name']}, SELL {stock1['name']}"]["deviation_from_std_error"],
            marker="^", color="green", label="Buy Signal", zorder=5
        )
        plt.scatter(
            df[df["signal"] == f"SELL {stock2['name']}, BUY {stock1['name']}"].index,
            df[df["signal"] == f"SELL {stock2['name']}, BUY {stock1['name']}"]["deviation_from_std_error"],
            marker="v", color="red", label="Sell Signal", zorder=5
        )
        plt.title(f"Deviation from Std Error: {stock2['name']} vs {stock1['name']}")
        plt.xlabel("Date")
        plt.ylabel("Deviation (in Std Errors)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plot_path = f"{save_dir}/spread_{stock1['name']}_{stock2['name']}.png"
        plt.savefig(plot_path)
        plt.close()
        upload_to_drive(f"spread_{stock1['name']}_{stock2['name']}.png", plot_path, folder_id)
        logger.info(f"Saved plot to {plot_path} and uploaded to Google Drive")

    if all_signals:
        signals_df = pd.concat(all_signals, ignore_index=True)
        signals_csv_path = f"{save_dir}/pair_trading_signals.csv"
        signals_df.to_csv(signals_csv_path, index=False)
        upload_to_drive("pair_trading_signals.csv", signals_csv_path, folder_id)
        logger.info(f"All signals saved to {signals_csv_path} and uploaded to Google Drive")
        send_email(signals_csv_path)
    else:
        logger.warning("No trading signals generated")

if __name__ == "__main__":
    main()
