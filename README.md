# İllüstratörler Kataloğu

Bugün hâlâ üreten 100 çağdaş illüstratör ve her birinden 25 eser: toplam 2.500 eser. Sanatçılar beş kategoriye ayrılır:

| Kategori | Sanatçı |
|---|---|
| Resimli Kitap | 10 |
| Çizgi Roman & Manga | 10 |
| Film/Oyun & Fantastik | 10 |
| Editoryal | 20 |
| Afiş & Grafik | 50 |

Afiş & Grafik; afişin yanında albüm kapağı, kurumsal kimlik, tipografi, jenerik ve sokak sanatı ustalarını da kapsar.

Canlı adres: https://illustratorler.vercel.app

## Mimari

```
index.html            Tek sayfalık arayüz (HTML + CSS + JS bir arada)
data/katalog.json     Sitenin okuduğu derlenmiş veri
kaynak/*.txt          Elle düzenlenen kaynak dosyalar
kaynak-arsiv/         Katalogdan çıkarılmış ama verisi saklanan sanatçılar
scripts/derle.py      kaynak/ → data/katalog.json derleyicisi ve doğrulayıcısı
yayinla.sh            Derle + Vercel'e dağıt + sabit adresi bağla
vercel.json           Başlıklar ve önbellek ayarları
```

Kaynak dosya biçimi:

```
= kategori-id
@ slug | Ad | yıllar | ülke | telif
# etiket · etiket · etiket
> Kısa biyografi.
- Başlık | alt başlık (özgün ad · not) | yıl | tür
```

`derle.py` her çalıştığında şunları denetler ve hata varsa JSON yazmaz:

- her sanatçının tam 25 eseri olması,
- slug'ların tekrar etmemesi,
- bir sanatçının eser başlıklarının (noktalama ve büyük/küçük harf yok sayılarak) tekrar etmemesi,
- her sanatçının tanımlı bir kategoriye bağlı olması.

Sanatçılar kategori, sonra doğum yılına; eserler yıla göre sıralanır.

## Tasarım kararları

- **Hepsi çağdaş.** Katalogdaki herkes yaşıyor ve ana üretimi 1980 sonrasına düşüyor. Bu tarihten önce başlayıp bugün de üretenler (Peter Blake, Tadanori Yokoo, Seymour Chwast gibi) dahil.
- **Görsel yok.** Bütün eserler telifli olduğu için hiçbir görsel kopyalanmadı. Her eser kartı, o eserin görsel aramasını yeni sekmede açar.
- **Doğrulanabilir eser listesi.** Her eser yılı ve türüyle birlikte yazıldı; 25 belgelenmiş eser bulunamayan sanatçılar katalog dışında bırakıldı.
- **Türkçe başlık + özgün ad.** Türkçede bilinen adı olan eserler Türkçe başlıkla, özgün adı alt satırda verilir. Çizgi roman, manga ve albüm adları çoğunlukla özgün haliyle kalır.
- **Arayüz korunuyor.** Kategori renkleri, içindekiler, arama ve filtre çipleri ilk katalog arayüzünün aynısı.

## Kullanım

Yerelde önizleme:

```bash
/usr/bin/python3 scripts/derle.py
python3 -m http.server 8000   # http://localhost:8000
```

Sanatçı eklemek ya da değiştirmek için ilgili `kaynak/*.txt` dosyasını düzenleyin, sonra:

```bash
bash yayinla.sh
```

Betik önce katalogu derler, doğrulama hatası varsa durur; geçerse production'a dağıtır ve `illustratorler.vercel.app` adresini yeni sürüme bağlar.
