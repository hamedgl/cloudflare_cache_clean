import requests
import argparse
from urllib.parse import urlparse


def get_zone_id(email, api_key, domain):
    url = f"https://api.cloudflare.com/client/v4/zones?name=https://{domain}&per_page=1"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get('result'):
        return data['result'][0]['id']
    else:
        print(f"Error getting zone ID for domain {domain}")
        return None


def purge_cache(email, api_key, zone_id, urls):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "files": urls
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Cache cleared successfully for zone ID {zone_id}")
    else:
        print(f"Error clearing cache for zone ID {zone_id}")


def main():
    parser = argparse.ArgumentParser(description="Clear Cloudflare cache for specified URLs.")
    parser.add_argument("--email", required=True, help="Cloudflare account email")
    parser.add_argument("--api_key", required=True, help="Cloudflare API key")
    parser.add_argument("--urls", nargs='+', required=True, help="Space-separated list of URLs to clear cache for")

    args = parser.parse_args()

    for url in args.urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.split(":")[0] if parsed_url.netloc else parsed_url.path.split("/")[
            0]  # Extract domain from URL
        zone_id = get_zone_id(args.email, args.api_key, domain)

        if zone_id:
            confirm = input(f"Do you want to clear cache for {url}? (y/n): ")
            if confirm.lower() == 'y':
                purge_cache(args.email, args.api_key, zone_id, [url])
            else:
                print(f"Skipping cache clearance for {url}")


if __name__ == "__main__":
    main()
