# Haber Analizi

Bu proje, Turkish Network Times haber sitesinden haber çekmek, çekilen verileri analiz etmek ve kelime frekanslarını görselleştirmek için geliştirilmiştir.

## Kurulum

Proje bağımlılıklarını yüklemek için aşağıdaki komutları kullanabilirsiniz:

```bash
pip install -r requirements.txt
```
## Kullanım

Proje, Python dilinde yazılmıştır ve main.py dosyasını çalıştırarak kullanılabilir. Örnek kullanım :
```bash
python main.py
```
##
***update_date*** kolonuna göre gruplanmış verileri ekrana print edebilmek için 186. satırdaki (#) işaretini kaldırarak yorumdan çıkarınız. 
##

### Analiz Edilen Veri
Proje, Turkish Network Times haber sitesinin "Gündem" kategorisindeki sayfalardan toplam 50 sayfa boyunca haberleri çeker. Her sayfada 10 haber bulunmaktadır. Çektiği haberleri ise news koleksiyonunda MongoDB veritabanına kaydeder.

### Kelime Frekansı Grafiği
Proje, çekilen haberlerin metin içeriğini analiz ederek en çok kullanılan 10 kelimenin frekansını görselleştirir. Kelime frekansı grafiği word_frequency.png adlı dosyada kaydedilir. Aynı zamanda word_frequency koleksiyonunda MongoDB veritabanına kaydedilir.

### Log Bilgileri
Proje, çeşitli istatistikleri ve hataları logs/logs.log dosyasına kaydeder. Log dosyası, başarılı haber çekme sayısı, başarısız haber çekme sayısı ve diğer önemli bilgileri içerir.

### Analiz Sonuçları
Proje, çekilen haberlerin tarihine göre gruplanmış istatistikleri ekrana yazdırır. Bu bilgiler, stats koleksiyonunda MongoDB veritabanına kaydedilir.

---

#### İsteğe bağlı değişkenler

Aşağıda verilen hatayı log kaydında görüyorsanız kodun 25.satırında bulunan max_workers değişkenini düşürerek hatadan kurtulabilirsiniz fakat işlem süresi artar.

**WARNING**:urllib3.connectionpool:Connection pool is full, discarding connection: turkishnetworktimes.com. Connection pool size: 10