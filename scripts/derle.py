#!/usr/bin/env python3
"""kaynak/*.txt  +  data/gorseller.json  ->  data/katalog.json

Kaynak biçimi (satır başına bir kayıt):
  = kategori-id                           dosyanın kategorisi
  @ slug | Ad | yıllar | ülke | kamu|telif  yeni sanatçı
  # etiket · etiket · etiket               etiketler
  > biyografi metni                        (birden çok satır olabilir)
  - Başlık | alt başlık | yıl | tür [| ?commons sorgusu]
"""
import json, os, re, sys, unicodedata, datetime

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONEMLER = [
    dict(id="resimli-kitap", ad="Resimli Kitap", aralik="Çocuk ve gençlik kitapları", renk="#c9472b", acik="#f5dfd6",
         aciklama="Resimli kitaplar ve resimli romanlar: metinle resmin birlikte anlattığı sayfalar."),
    dict(id="cizgi-manga", ad="Çizgi Roman & Manga", aralik="Grafik roman, manga, anime", renk="#a8742a", acik="#f1e6d2",
         aciklama="Amerikan, Avrupa ve Japon çizgi anlatısı: süper kahramandan grafik romana, haftalık mangadan animeye."),
    dict(id="fantastik", ad="Film/Oyun & Fantastik", aralik="Kapak, konsept, karakter tasarımı", renk="#1d6f63", acik="#d9ebe7",
         aciklama="Fantastik ve bilimkurgu kapakları, film ve oyun dünyaları için kavramsal tasarım ve karakter çizimi."),
    dict(id="editoryal", ad="Editoryal", aralik="Dergi, gazete, karikatür", renk="#2f4a7a", acik="#e3e6ee",
         aciklama="Dergi kapakları, gazete çizimleri, karikatür ve çizgi röportaj: gündemi tek bir imgeye ya da sayfaya sığdıran illüstrasyon."),
    dict(id="afis-grafik", ad="Afiş & Grafik", aralik="Afiş, albüm, kimlik, tipografi", renk="#8a3b6b", acik="#efdde8",
         aciklama="Film ve konser afişleri, albüm kapakları, kurumsal kimlikler, tipografi ve sokak grafiği: tasarımla illüstrasyonun kesiştiği alan."),
]

def kisa(s):
    s = unicodedata.normalize("NFKD", s.replace("ı", "i").replace("İ", "I")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48]

def oku():
    sanatcilar, hatalar = [], []
    for ad in sorted(os.listdir(os.path.join(KOK, "kaynak"))):
        if not ad.endswith(".txt"):
            continue
        donem, a = None, None
        for no, satir in enumerate(open(os.path.join(KOK, "kaynak", ad), encoding="utf-8"), 1):
            satir = satir.rstrip("\n").strip()
            if not satir or satir.startswith("//"):
                continue
            tip, govde = satir[0], satir[1:].strip()
            yer = "%s:%d" % (ad, no)
            if tip == "=":
                donem = govde
            elif tip == "@":
                p = [x.strip() for x in govde.split("|")]
                if len(p) != 5:
                    hatalar.append(yer + " sanatçı satırı 5 alan olmalı"); continue
                a = dict(slug=p[0], ad=p[1], yillar=p[2], ulke=p[3], donem=donem, kamu=(p[4] == "kamu"),
                         etiketler=[], bio="", eserler=[])
                sanatcilar.append(a)
            elif tip == "#":
                a["etiketler"] = [x.strip() for x in govde.split("·") if x.strip()]
            elif tip == ">":
                a["bio"] = (a["bio"] + " " + govde).strip()
            elif tip == "-":
                p = [x.strip() for x in govde.split("|")]
                if len(p) not in (4, 5):
                    hatalar.append(yer + " eser satırı 4-5 alan olmalı: " + govde[:60]); continue
                w = dict(baslik=p[0], alt=p[1], yil=p[2], tur=p[3])
                if len(p) == 5 and p[4].startswith("?"):
                    w["sorgu"] = p[4][1:].strip()
                w["anahtar"] = a["slug"] + "/" + kisa(p[0])
                a["eserler"].append(w)
            else:
                hatalar.append(yer + " tanınmayan satır")
    return sanatcilar, hatalar

def main():
    sanatcilar, hatalar = oku()
    sira = {d["id"]: i for i, d in enumerate(DONEMLER)}
    for a in sanatcilar:
        if a["donem"] not in sira: hatalar.append("%s: bilinmeyen kategori %s" % (a["slug"], a["donem"]))
    dogum = lambda a: int((re.findall(r"\d{4}", a["yillar"]) or ["9999"])[0])
    sanatcilar.sort(key=lambda a: (sira.get(a["donem"], 99), dogum(a), a["ad"]))
    gp = os.path.join(KOK, "data", "gorseller.json")
    gorseller = json.load(open(gp, encoding="utf-8")) if os.path.exists(gp) else {}
    EN_AZ = 10
    sluglar, uyari = set(), []
    for a in sanatcilar:
        if a["slug"] in sluglar: hatalar.append("tekrar eden slug: " + a["slug"])
        sluglar.add(a["slug"])
        if len(a["eserler"]) < EN_AZ: hatalar.append("%s: yalnızca %d eser (en az %d)" % (a["slug"], len(a["eserler"]), EN_AZ))
        anahtarlar = [w["anahtar"] for w in a["eserler"]]
        if len(set(anahtarlar)) != len(anahtarlar): hatalar.append("tekrar eden eser başlığı: " + a["slug"])
        if not a["bio"]: uyari.append(a["slug"] + ": biyografi yok")
        for w in a["eserler"]:
            g = gorseller.get(w["anahtar"])
            if g and g.get("dosya") and os.path.exists(os.path.join(KOK, g["dosya"])):
                w["gorsel"], w["kaynak"] = g["dosya"], g.get("kaynak", "")
                if g.get("tarih"):
                    w["tarih"] = g["tarih"]
                if g.get("secki"):
                    w["secki"] = True
            w.pop("sorgu", None); w.pop("anahtar", None)
        # Dönem ve seri kayıtlarını ilk yayın yılına göre sırala.
        def tarih(w):
            yil = re.search(r"\d{4}", w["yil"])
            return w.get("tarih") or (yil.group() if yil else "")
        a["eserler"].sort(key=tarih, reverse=True)
    if hatalar:
        print("HATA:\n  " + "\n  ".join(hatalar)); sys.exit(1)
    for u in uyari: print("uyarı:", u)
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    bugun = datetime.date.today()
    cikti = dict(guncelleme="%d %s %d" % (bugun.day, aylar[bugun.month-1], bugun.year),
                 donemler=DONEMLER, sanatcilar=sanatcilar)
    json.dump(cikti, open(os.path.join(KOK, "data", "katalog.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    eser = sum(len(a["eserler"]) for a in sanatcilar)
    gor = sum(1 for a in sanatcilar for w in a["eserler"] if w.get("gorsel"))
    print("derlendi: %d sanatçı, %d eser, %d görsel" % (len(sanatcilar), eser, gor))

if __name__ == "__main__":
    main()
