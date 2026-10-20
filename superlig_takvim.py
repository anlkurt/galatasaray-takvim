#!/usr/bin/env python3
"""Galatasaray'ın Süper Lig maçlarını abone olunabilir bir .ics takvimine dönüştürür.

Ana kaynak TFF'nin resmi haftalık fikstür sayfasıdır (saat değişiklikleri önce burada
görünür). TFF'ye ulaşılamazsa ESPN'in fikstür verisi yedek olarak kullanılır.

Kullanım:
    python3 superlig_takvim.py              # docs/galatasaray.ics üretir
    python3 superlig_takvim.py --kaynak espn

Sadece Python standart kütüphanesi kullanılır.
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

TAKIM = "galatasaray"
HAFTA_SAYISI = 34
MAC_SURESI = timedelta(hours=2)
HATIRLATMA = "-PT1H"  # maçtan 1 saat önce
ISTANBUL = timezone(timedelta(hours=3))  # Türkiye 2016'dan beri sabit UTC+3
CIKTI = Path(__file__).resolve().parent / "docs" / "galatasaray.ics"

TFF_HAFTA = "https://www.tff.org/Default.aspx?pageID=198&hafta={}"
ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/teams/432/schedule"

# Kaynaklardaki farklı yazımları (ör. "TÜMOSAN KONYASPOR", "Konyaspor") tek anahtara indirger.
# Anahtar, sadeleştirilmiş takım adının içinde geçen parçadır; değer takvimde görünen addır.
TAKIMLAR = {
    "galatasaray": "Galatasaray",
    "fenerbahce": "Fenerbahçe",
    "besiktas": "Beşiktaş",
    "trabzonspor": "Trabzonspor",
    "basaksehir": "Başakşehir",
    "kasimpasa": "Kasımpaşa",
    "konyaspor": "Konyaspor",
    "rizespor": "Çaykur Rizespor",
    "gaziantep": "Gaziantep FK",
    "alanyaspor": "Alanyaspor",
    "genclerbirligi": "Gençlerbirliği",
    "goztepe": "Göztepe",
    "samsunspor": "Samsunspor",
    "eyupspor": "Eyüpspor",
    "kocaelispor": "Kocaelispor",
    "erzurum": "Erzurumspor FK",
    "amed": "Amedspor",
    "corum": "Çorum FK",
    "antalyaspor": "Antalyaspor",
    "kayserispor": "Kayserispor",
    "sivasspor": "Sivasspor",
    "hatayspor": "Hatayspor",
    "adanademirspor": "Adana Demirspor",
    "bodrum": "Bodrum FK",
    "karagumruk": "Fatih Karagümrük",
}


def sade(metin):
    tablo = str.maketrans("çğıöşüÇĞİÖŞÜâÂ", "cgiosuCGIOSUaA")
    return re.sub(r"[^a-z0-9]", "", metin.translate(tablo).lower())


def takim_anahtari(ad):
    s = sade(ad)
    for anahtar in TAKIMLAR:
        if anahtar in s:
            return anahtar
    return s  # bilinmeyen takım: sadeleştirilmiş adıyla devam et


def getir(url, deneme=3):
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (galatasaray-takvim)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:  # ağ hatasında kısa bekleyip tekrar dene
            if i == deneme - 1:
                raise RuntimeError("{} alınamadı: {}".format(url, e))
            time.sleep(2 * (i + 1))


# ---------------------------------------------------------------- TFF

def tff_maclari():
    maclar = []
    for hafta in range(1, HAFTA_SAYISI + 1):
        sayfa = getir(TFF_HAFTA.format(hafta)).decode("windows-1254", errors="replace")
        satirlar = re.findall(r'<tr class="haftaninMaclariTr">(.*?)</tr>', sayfa, re.S)
        if not satirlar:
            raise RuntimeError("TFF {}. hafta sayfasında maç bulunamadı".format(hafta))
        for satir in satirlar:
            def alan(ad):
                m = re.search(ad + r'">([^<]*)<', satir)
                return html.unescape(m.group(1)).strip() if m else ""

            ev, dep = takim_anahtari(alan("Label4")), takim_anahtari(alan("Label1"))
            if TAKIM not in (ev, dep):
                continue
            tarih, saat = alan("lblTarih"), alan("lblSaat")
            gun = datetime.strptime(tarih, "%d.%m.%Y")
            if saat:
                bas = datetime.strptime(tarih + " " + saat, "%d.%m.%Y %H:%M")
                bas = bas.replace(tzinfo=ISTANBUL).astimezone(timezone.utc)
            else:
                bas = None
            g1, g2 = alan("Label5"), alan("Label6")
            maclar.append({
                "hafta": hafta,
                "ev": ev,
                "deplasman": dep,
                "gun": gun.date(),
                "baslangic": bas,
                "skor": "{}-{}".format(g1, g2) if g1 and g2 else None,
                "stat": "",
                "kaynak": "TFF",
            })
    return maclar


# ---------------------------------------------------------------- ESPN (yedek)

def espn_maclari():
    olaylar = {}
    for ek in ("", "?fixture=true"):
        for e in json.loads(getir(ESPN + ek)).get("events", []):
            olaylar[e["id"]] = e
    maclar = []
    for e in sorted(olaylar.values(), key=lambda e: e["date"]):
        comp = e["competitions"][0]
        taraf = {c["homeAway"]: c for c in comp["competitors"]}
        bas = datetime.strptime(e["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        skor = None
        if comp["status"]["type"].get("completed"):
            skor = "{}-{}".format(*(int(float(taraf[k]["score"]["value"])) for k in ("home", "away")))
        maclar.append({
            "hafta": None,
            "ev": takim_anahtari(taraf["home"]["team"]["displayName"]),
            "deplasman": takim_anahtari(taraf["away"]["team"]["displayName"]),
            "gun": bas.astimezone(ISTANBUL).date(),
            "baslangic": bas if comp.get("timeValid", True) else None,
            "skor": skor,
            "stat": comp.get("venue", {}).get("fullName", ""),
            "kaynak": "ESPN",
        })
    for i, m in enumerate(maclar, 1):  # ESPN hafta bilgisi vermiyor; sıradan çıkar
        m["hafta"] = i
    return maclar


# ---------------------------------------------------------------- ICS

def kacis(metin):
    return metin.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def katla(satir):
    """RFC 5545: satırları 75 oktette katlar, UTF-8 karakterlerini bölmeden."""
    b = satir.encode("utf-8")
    parcalar = []
    while len(b) > 75:
        kes = 75 if not parcalar else 74
        while (b[kes] & 0xC0) == 0x80:
            kes -= 1
        parcalar.append(b[:kes].decode("utf-8"))
        b = b[kes:]
    parcalar.append(b.decode("utf-8"))
    return "\r\n ".join(parcalar)


def ics_olustur(maclar, sezon):
    simdi = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    s = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//galatasaray-takvim//TR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Galatasaray - Süper Lig",
        "X-WR-TIMEZONE:Europe/Istanbul",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]
    for m in maclar:
        ev, dep = TAKIMLAR.get(m["ev"], m["ev"]), TAKIMLAR.get(m["deplasman"], m["deplasman"])
        baslik = "{} {} {}".format(ev, m["skor"], dep) if m["skor"] else "{} - {}".format(ev, dep)
        aciklama = ["Trendyol Süper Lig {}. hafta".format(m["hafta"])]
        if m["baslangic"] is None:
            baslik += " (saat belli değil)"
            aciklama.append("Maç saati henüz açıklanmadı; açıklanınca otomatik güncellenir.")
        aciklama.append("Kaynak: " + m["kaynak"])

        # UID ev sahibi + deplasmandan türetilir: her eşleşme sezonda bir kez olur ve
        # kaynak (TFF/ESPN) değişse bile aynı kalır, böylece çift kayıt oluşmaz.
        s += [
            "BEGIN:VEVENT",
            "UID:{}-{}-{}@galatasaray-takvim".format(sezon, m["ev"], m["deplasman"]),
            "DTSTAMP:" + simdi,
        ]
        if m["baslangic"]:
            s += [
                "DTSTART:" + m["baslangic"].strftime("%Y%m%dT%H%M%SZ"),
                "DTEND:" + (m["baslangic"] + MAC_SURESI).strftime("%Y%m%dT%H%M%SZ"),
            ]
        else:
            s += [
                "DTSTART;VALUE=DATE:" + m["gun"].strftime("%Y%m%d"),
                "DTEND;VALUE=DATE:" + (m["gun"] + timedelta(days=1)).strftime("%Y%m%d"),
                "TRANSP:TRANSPARENT",
            ]
        s += [
            "SUMMARY:" + kacis(baslik),
            "DESCRIPTION:" + kacis("\n".join(aciklama)),
        ]
        if m["stat"]:
            s.append("LOCATION:" + kacis(m["stat"]))
        if m["baslangic"] and not m["skor"]:
            s += [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                "DESCRIPTION:" + kacis(baslik + " 1 saat sonra başlıyor"),
                "TRIGGER:" + HATIRLATMA,
                "END:VALARM",
            ]
        s.append("END:VEVENT")
    s.append("END:VCALENDAR")
    return "\r\n".join(katla(x) for x in s) + "\r\n"


def sezon_adi(maclar):
    yil = maclar[0]["gun"].year
    return "{}-{}".format(yil, yil + 1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kaynak", choices=["tff", "espn"], default="tff")
    p.add_argument("--cikti", type=Path, default=CIKTI)
    args = p.parse_args()

    maclar = []
    if args.kaynak == "tff":
        try:
            maclar = tff_maclari()
        except Exception as e:
            print("TFF kullanılamadı ({}); ESPN'e geçiliyor.".format(e), file=sys.stderr)
    if not maclar:
        maclar = espn_maclari()
    if len(maclar) < 30:
        sys.exit("Sadece {} maç bulundu; mevcut takvim korunuyor.".format(len(maclar)))

    args.cikti.parent.mkdir(parents=True, exist_ok=True)
    with open(args.cikti, "w", encoding="utf-8", newline="") as f:
        f.write(ics_olustur(maclar, sezon_adi(maclar)))
    print("{}: {} maç ({})".format(args.cikti, len(maclar), maclar[0]["kaynak"]))


if __name__ == "__main__":
    main()
