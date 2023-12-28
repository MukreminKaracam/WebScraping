import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter
import pymongo
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Web scraping işlemleri için gerekli değişkenler
BASE_URL = "https://turkishnetworktimes.com/kategori/gundem/"
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "mukremin_karacam"
page_count = 50

# Log dosyası konfigürasyonu
logging.basicConfig(filename="logs/logs.log", level=logging.INFO)

# MongoDB bağlantısı
client = pymongo.MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Threading için ThreadPool
thread_pool = ThreadPoolExecutor(max_workers=10) 

# Thread safety için Lock
counter_lock = Lock()

# Verimlilik ölçümleri
start_time = datetime.now()
success_count = 0
fail_count = 0
total_requests = 0

# Session oluştur
session = requests.Session()

def scrape_news(news_url):
    global total_requests
    total_requests += 1
    
    if db['news'].count_documents({'url': news_url}) > 0:
        logging.info(f"Skipping duplicate news: {news_url}")
        return
    
    try:
        response = session.get(news_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Haber verilerini çekme işlemleri burada yapılacak
        url = news_url
        # Header,summary ve text çekme
        header = soup.select_one('h1.single_title').text.strip()
        summary = soup.select_one('.single_excerpt').text.strip()
        text = ' '.join(p.text.strip() for p in soup.select('.yazi_icerik'))
        # Image url ve tarih çekme
        img_element = soup.select_one('.onresim.wp-post-image')
        img_url_list = [img_element['src']] if img_element else []
        publish_date = soup.select_one('time')['datetime']
        update_date = soup.select_one('time')['datetime']

        news_data = {
            'url': url,
            'header': header,
            'summary': summary,
            'text': text,
            'img_url_list': img_url_list,
            'publish_date': publish_date,
            'update_date': update_date
        }

        # Veritabanına kaydetme
        save_to_mongodb(news_data)

        # Başarı durumu güncelleme
        with counter_lock:
            global success_count
            success_count += 1
    except Exception as e:
        # Hata durumu güncelleme
        with counter_lock:
            global fail_count
            fail_count += 1
            logging.error(f"Haber çekme hatası: {e}")

def analyze_text(news_data_list):
    analyzed_data = []
    for news_data in news_data_list:
        analyzed_data.extend(news_data['text'].split())
    return analyzed_data

def plot_word_frequency(word_frequency):
    # Kelime frekansı grafiğini oluşturma işlemi burada yapılacak
    most_common_words = dict(word_frequency.most_common(10))
    plt.bar(most_common_words.keys(), most_common_words.values())
    plt.xlabel('Kelimeler')
    plt.ylabel('Frekans')
    plt.title('En Çok Kullanılan Kelimeler')
    plt.xticks(rotation=45)
    plt.savefig('word_frequency.png')
    plt.close()

def save_to_mongodb(news_data):
    # MongoDB'ye kaydetme işlemleri burada yapılacak
    news_collection = db['news']
    news_collection.insert_one(news_data)

def save_word_frequency_to_mongodb(word_frequency):
    # word_frequency_collection'e ekleme
    word_frequency_collection = db['word_frequency']

    # word_frequency sözlüğü boş değilse ve içinde eleman varsa
    if word_frequency:
        most_common_words = dict(word_frequency.most_common(10))
        word_frequency_collection.insert_many([{'word': word, 'count': count} for word, count in most_common_words.items()])
    else:
        logging.warning("Word frequency dictionary is empty. No data inserted.")

def save_stats_to_mongodb():
    # Verimlilik ölçümlerini kaydetme
    elapsed_time = datetime.now() - start_time
    stats_collection = db['stats']
    stats_collection.insert_one({
        'elapsed_time': elapsed_time.total_seconds(),
        'count': total_requests,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'success_count': success_count,
        'fail_count': fail_count
    })

def log_stats():
    # Loglama işlemleri burada yapılacak
    logging.info(f"Toplam başarılı haber çekme sayısı: {success_count}")
    logging.info(f"Toplam başarısız haber çekme sayısı: {fail_count}")

def print_grouped_data_by_update_date():
    # update_date'e göre gruplanmış verileri ekrana print etme işlemi burada yapılacak
    grouped_data = db['news'].aggregate([
        {'$group': {'_id': '$update_date', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ])

    for data in grouped_data:
        print(f"Update Date: {data['_id']}, Count: {data['count']}")

def main():
    # MongoDB koleksiyonunu tanımla
    news_collection = db['news']

    # Haber sitenin belirli sayfa sayısındaki haberleri çekme işlemi
    for page_number in range(1, page_count + 1):
        page_url = f"{BASE_URL}page/{page_number}/"
        response = session.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        kategori_yazilist_divs = soup.find_all("div", class_="kategori_yazilist")
        row_divs = [div.find("div", class_="row") for div in kategori_yazilist_divs if div.find("div", class_="row")]

        # Her bir haber <div>'indeki bağlantıları çek
        for row_div in row_divs:
            haber_post_divs = row_div.find_all("div", class_="haber-post")
            for haber_post_div in haber_post_divs:
                link = haber_post_div.find("a", class_="post-link")
                if link:
                    thread_pool.submit(scrape_news, link['href'])
    else:
        print(f"Sayfa sınırına ulaşıldı(50)")   
        logging.info(f"Sayfa {page_url} yüklenirken bir hata oluştu. HTTP Kodu: {response.status_code}")
        
    # Analiz yapma işlemi
    news_data_list = list(news_collection.find())
    analyzed_data = analyze_text(news_data_list)

    # Kelime frekansı grafiği oluşturma işlemi
    word_frequency = Counter(analyzed_data)
    plot_word_frequency(word_frequency)

    # Kelime sıklığı MongoDB'ye kaydetme işlemleri
    save_word_frequency_to_mongodb(word_frequency)
    save_stats_to_mongodb()

    # Loglama işlemleri
    log_stats()

if __name__ == "__main__":
    #print_grouped_data_by_update_date() 
    main()