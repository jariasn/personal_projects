import requests
import json

def fetch_kraken_assets():
    """Fetch asset information from Kraken's API."""
    url = "https://api.kraken.com/0/public/Assets"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        raise Exception(f"Error fetching assets: {response.status_code} - {response.text}")

def fetch_kraken_asset_pairs():
    """Fetch asset pair information from Kraken's API."""
    url = "https://api.kraken.com/0/public/AssetPairs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        raise Exception(f"Error fetching asset pairs: {response.status_code} - {response.text}")

def create_asset_mapping(assets, asset_pairs):
    """Create a mapping of asset symbols to their common names and trading pairs."""
    asset_mapping = {}

    # Map asset symbols to their alternative names
    for symbol, details in assets.items():
        altname = details.get('altname')
        if altname:
            asset_mapping[altname] = symbol

    # Map trading pairs to their WebSocket names
    pair_mapping = {}
    for pair, details in asset_pairs.items():
        wsname = details.get('wsname')
        if wsname:
            pair_mapping[wsname] = pair

    return {
        "assets": asset_mapping,
        "pairs": pair_mapping
    }

def save_to_json(data, filename):
    """Save the data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

def main():
    try:
        assets = fetch_kraken_assets()
        asset_pairs = fetch_kraken_asset_pairs()
        mapping = create_asset_mapping(assets, asset_pairs)
        save_to_json(mapping, 'kraken_asset_mapping.json')
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()