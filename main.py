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
