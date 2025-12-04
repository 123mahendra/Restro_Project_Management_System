import requests

def get_hsl_info():
    response = requests.get("https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql")
    return response.json()
