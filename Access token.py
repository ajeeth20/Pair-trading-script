from kiteconnect import KiteConnect
import pickle

api_key = "ry60l4ib8p0189sn"
api_secret = "yyfmwm3s8hcuhnhodu5ugnhjfqcmstmx"
request_token = "2ePKKGhqQ2fhtbTWMf14qQEWWQLtGE5L"

kite = KiteConnect(api_key=api_key)

# Get access token
data = kite.generate_session(request_token, api_secret=api_secret)
access_token = data["access_token"]
kite.set_access_token(access_token)

# Save it for reuse
with open("/tmp/access_token.pkl", "wb") as f:
    pickle.dump(access_token, f)

print("Access Token Saved Successfully!")
