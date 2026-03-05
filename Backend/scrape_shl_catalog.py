import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

DELAY = 0.8   # polite delay between requests


# --------------------------------------------------
# SAFE REQUEST FUNCTION (WITH RETRY)
# --------------------------------------------------
def safe_request(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)

            if response.status_code == 200:
                return response

            print(f"Retry {attempt+1} - Status:", response.status_code)
            time.sleep(2)

        except Exception as e:
            print("Request error:", e)
            time.sleep(2)

    return None


# --------------------------------------------------
# STEP 1: GET ALL VALID PRODUCT LINKS
# --------------------------------------------------
def get_product_links():
    print("Opening catalog pages...\n")

    product_links = set()
    start = 0

    while True:
        url = f"{CATALOG_URL}?start={start}"
        print("Checking page:", url)

        response = safe_request(url)
        if not response:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        found_on_page = 0

        for link in links:
            href = link["href"]

            if "/products/product-catalog/" in href and "/view/" in href:

                full_url = BASE_URL + href if href.startswith("/") else href
                full_url = full_url.split("?")[0].rstrip("/")

                # Remove unwanted pages
                if any(x in full_url.lower() for x in [
                    "report",
                    "practice",
                    "sample",
                    "brochure"
                ]):
                    continue

                product_links.add(full_url)
                found_on_page += 1

        print("Products found on this page:", found_on_page)

        if found_on_page == 0:
            break

        start += 12
        time.sleep(DELAY)

    print("\nTotal unique product links found:", len(product_links))
    return list(product_links)


# --------------------------------------------------
# STEP 2: SCRAPE PRODUCT DETAILS
# --------------------------------------------------
def scrape_product(url):
    response = safe_request(url)
    if not response:
        print("Skipping (failed):", url)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Product Name
    name_tag = soup.find("h1")
    name = name_tag.get_text(strip=True) if name_tag else ""

    # Meta Description
    desc_tag = soup.find("meta", {"name": "description"})
    description = desc_tag["content"].strip() if desc_tag else ""

    # Try extracting key product info section
    details_text = ""
    details_section = soup.find("div", class_="product-details")
    if details_section:
        details_text = details_section.get_text(separator=" | ", strip=True)

    return {
        "Product Name": name,
        "URL": url,
        "Description": description,
        "Details": details_text
    }


# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    print("\n===== SHL PRODUCT CATALOG SCRAPER STARTED =====\n")

    product_urls = get_product_links()

    print("\nScraping product pages...\n")

    data = []

    for i, url in enumerate(product_urls):
        print(f"Scraping {i+1}/{len(product_urls)}")

        product = scrape_product(url)
        if product:
            data.append(product)

        time.sleep(DELAY)

    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["URL"], inplace=True)

    print("\nFinal unique products:", len(df))

    df.to_csv("shl_product_catalog_cleaned.csv", index=False)
    print("Saved as shl_product_catalog_cleaned.csv")

    print("\n===== SCRAPING COMPLETED SUCCESSFULLY =====")


if __name__ == "__main__":
    main()