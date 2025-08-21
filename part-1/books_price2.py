import re
import csv
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

def scrape_page(session, url):
    """Scraper une page et retourner la liste des livres + prix total."""
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    books = soup.find("ol", class_="row").find_all("li")
    resultats = []
    total_price = 0

    for li in books:
        article = li.find("article", class_="product_pod")
        relative_link = article.h3.a["href"]  # lien relatif
        book_url = urljoin(url, relative_link)  # lien absolu

        # Aller à la page du livre
        response = session.get(book_url)
        response.raise_for_status()
        book_soup = BeautifulSoup(response.text, 'html.parser')

        # Titre
        titre = book_soup.find("div", class_="product_main").find("h1").text.strip()

        # Prix
        book_price = book_soup.find("p", class_="price_color").text
        book_price = float(re.findall(r"£\d+\.\d+", book_price)[0][1:])

        # Stock
        book_stock_text = book_soup.find("p", class_="instock availability").text.strip()
        stock_number = int(re.findall(r"\d+", book_stock_text)[0])

        # Prix total de ce livre (stock × prix)
        book_total_price = stock_number * book_price
        total_price += book_total_price

        resultats.append({
            "titre du livre": titre,
            "prix du livre": book_price,
            "stock": stock_number,
            "prix du stock de chaque livre": book_total_price
        })

    return resultats, total_price


def main():
    all_results = []
    total_general = 0

    with requests.Session() as session:
        for i in range(1, 3):  # il y a 50 pages
            if i == 1:
                url = BASE_URL + "index.html"
            else:
                url = BASE_URL + f"catalogue/page-{i}.html"

            print(f"Scraping de la page {i} ...")
            livres, total_page = scrape_page(session, url)
            all_results.extend(livres)
            total_general += total_page

    # Sauvegarde CSV
    with open("livres.csv", "w", newline="", encoding="utf-8") as fichier:
        colonnes = ["titre du livre", "prix du livre", "stock", "prix du stock de chaque livre"]
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(all_results)

    print(f"\n💰 Le prix total de TOUS les livres est : {total_general:.2f} £")


if __name__ == '__main__':
    main()
