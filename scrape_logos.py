import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set a custom User-Agent header to mimic a browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

failed_urls = []

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        # Create a modern default context for server authentication.
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # If available, force TLSv1.2 only.
        if hasattr(context, 'minimum_version'):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_2
        # Optionally relax the cipher security level if needed.
        try:
            context.set_ciphers("DEFAULT:@SECLEVEL=1")
        except Exception as e:
            print("Error setting ciphers:", e)
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs
        )


def get_logo_url(domain: str) -> str:
    url = get_logo_url_2(domain)

    if not url:
        url = get_logo_url_2(f"https://{domain}")

    return url

def get_logo_url_2(domain: str) -> str:
    clearbit_url = f"https://logo.clearbit.com/{domain}"
    try:
        session = requests.Session()
        session.mount("https://", TLSAdapter())
        response = session.get(clearbit_url, timeout=10, headers=HEADERS)
        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            return clearbit_url
    except Exception as e:
        print(f"Clearbit lookup failed for {domain}: {e}")

    # Ensure the domain has a scheme (http://) if missing
    url = domain if domain.startswith("http") else f"http://{domain}"
    try:
        session = requests.Session()
        session.mount("https://", TLSAdapter())
        response = session.get(url, timeout=10, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    icon_tags = soup.find_all("link", rel=lambda x: x and "icon" in x.lower())
    logo_href = None

    if icon_tags:
        # Prefer SVG icons if available
        for tag in icon_tags:
            href = tag.get("href")
            if href and "svg" in href.lower():
                logo_href = href
                break
        if not logo_href:
            logo_href = icon_tags[0].get("href")
    else:
        logo_href = "/favicon.ico"

    return urljoin(url, logo_href)


def download_logo(domain: str, logo_url: str) -> str:
    """
    Downloads the logo from the specified URL and saves it as <domain>.<extension>.
    Returns the file path if successful, or None on failure.
    """
    try:
        session = requests.Session()
        session.mount("https://", TLSAdapter())
        response = session.get(logo_url, stream=True, timeout=10, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"Error downloading logo from {logo_url} for {domain}: {e}")
        return None

    # Determine file extension
    parsed = urlparse(logo_url)
    extension = os.path.splitext(parsed.path)[1]  # e.g., .png, .ico, etc.
    allowed_extensions = [".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico"]

    if extension.lower() not in allowed_extensions:
        content_type = response.headers.get("content-type", "")
        if "svg" in content_type:
            extension = ".svg"
        elif "png" in content_type:
            extension = ".png"
        elif "jpeg" in content_type or "jpg" in content_type:
            extension = ".jpg"
        else:
            extension = ".ico"

    filename = f"{domain}{extension}"
    logo_filepath = os.path.join("logos", filename)
    try:
        with open(logo_filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return logo_filepath
    except Exception as e:
        print(f"Error saving logo to {logo_filepath} for {domain}: {e}")
        return None


def download_images():
    df = pq.read_table(source="./logos.snappy.parquet").to_pandas()
    os.makedirs("logos", exist_ok=True)

    def download_row(row):
        domain = row["domain"]
        logo_url = get_logo_url(domain)
        if not logo_url:
            print(f"No logo found for {domain}")
            failed_urls.append(domain)
            return

        result = download_logo(domain, logo_url)
        if not result:
            failed_urls.append(domain)

    with ThreadPoolExecutor(max_workers=128) as executor:
        futures = [executor.submit(download_row, row) for _, row in df.iterrows()]
        for future in as_completed(futures):
            future.result()

    total = len(df)
    successful = total - len(failed_urls)
    success_percent = successful / total * 100

    with open("scrape_results.txt", "w") as result_file:
        result_file.write(f"Downloaded logos for {successful} domains out of {total} ({success_percent:.2f}%)\n")

    if failed_urls:
        with open("failed_domains.txt", "w") as f:
            for domain in failed_urls:
                f.write(domain + "\n")




def main():
    # print(get_logo_url("chicco.pl"))
    # print(download_logo("chicco.pl", get_logo_url("chicco.pl")))
    download_images()


if __name__ == "__main__":
    main()
