import requests
from bs4 import BeautifulSoup
import csv
import time
import os

def extract_products_details(row):
    details = {
        "Assessment Name": None,
        "Assessment URL": None,
        "Remote Testing Support": "N/A",
        "Adaptive/IRT Support": "N/A",
        "Test Type": "N/A",
        "Duration": "N/A"
    }
    try:
        title_cell = row.find("td", class_="custom__table-heading__title")
        if title_cell:
            link_tag = title_cell.find("a")
            if link_tag and 'href' in link_tag.attrs:
                details["Assessment URL"] = "https://www.shl.com" + link_tag['href']
                details["Assessment Name"] = link_tag.text.strip()

        general_cells = row.find_all("td", class_="custom__table-heading__general")
        if len(general_cells) >= 3:
            remote_span = general_cells[0].find("span", class_="catalogue__circle")
            if remote_span and "-yes" in remote_span.get('class', []):
                details["Remote Testing Support"] = "Yes"

            adaptive_span = general_cells[1].find("span", class_="catalogue__circle")
            if adaptive_span and "-yes" in adaptive_span.get("class", []):
                details["Adaptive/IRT Support"] = "Yes"

            test_type_cell = general_cells[2]
            test_type_spans = test_type_cell.find_all("span", class_="product-catalogue__key")
            if test_type_spans:
                test_types = [span.text.strip() for span in test_type_spans]
                details["Test Type"] = ", ".join(test_types)

    except AttributeError as e:
        print(f"AttributeError while parsing row: {e}")

    return details

def crawl_shl_catalog_listing(base_url, output_csv, delay=1):
    all_products_data = []
    start_value = 0
    increment = 12
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    while True:
        url = f"{base_url}?start={start_value}"
        print(f"Fetching page starting at: {start_value}: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            product_table_wrapper = soup.find("div", class_="custom__table-responsive")
            if not product_table_wrapper:
                print("No table wrapper found. Stopping.")
                break

            table = product_table_wrapper.find("table")
            if not table:
                print("No table found inside wrapper. Stopping.")
                break

            rows = table.find_all("tr")[1:]  # skip header
            print(f"Found {len(rows)} products on this page")

            if not rows:
                break

            for row in rows:
                product_info = extract_products_details(row)
                if product_info['Assessment URL']:
                    all_products_data.append(product_info)

            start_value += increment
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"Error in fetching page {url} : {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    if all_products_data:
        with open(output_csv, "w", newline='', encoding='utf-8') as f:
            fieldnames = ['Assessment Name', 'Assessment URL', 'Remote Testing Support',
                          'Adaptive/IRT Support', 'Test Type', 'Duration']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in all_products_data:
                writer.writerow(product)
        print(f"\nSuccessfully saved {len(all_products_data)} product listings to {output_csv}")
        return all_products_data
    else:
        print("No products found.")
        return []

def main():
    catalog_base_url = "https://www.shl.com/solutions/products/product-catalog/"
    output_csv = "shl_catalog_listing.csv"
    if os.path.exists(output_csv):
        print("File exists, content will be overwritten.")
    product_listings = crawl_shl_catalog_listing(catalog_base_url, output_csv=output_csv)

if __name__ == "__main__":
    main()
