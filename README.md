# Galatasaray Süper Lig Takvimi

Galatasaray'ın Trendyol Süper Lig maçlarını Apple Takvim'e abone olunabilir bir takvim
olarak ekler. Maç saatleri açıklandıkça veya değiştikçe takvim kendiliğinden güncellenir.
Her maçtan **1 saat** ve **5 dakika** önce hatırlatma gelir.

**Takvim adresi:** `https://anlkurt.github.io/galatasaray-takvim/galatasaray.ics`

## Apple Takvim'e ekleme

1. Mac'te Takvim → **Dosya → Yeni Takvim Aboneliği…** → adresi yapıştırın → Abone Ol.
2. Açılan pencerede:
   - **Konum:** iCloud (iPhone ve iPad'de de görünmesi için)
   - **Sil: Uyarıları** ve **Uyarıları yok say** kutuları **işaretsiz** olmalı (yoksa hatırlatmalar gelmez)
   - **Otomatik yenile:** Her saat

## Nasıl çalışır?

- `superlig_takvim.py` maçları **TFF** fikstür sayfalarından ve **ESPN**'den çekip
  birleştirir. Saat için TFF esas alınır, TFF'de saat yoksa ESPN'inki kullanılır.
  Kaynaklardan biri çalışmazsa takvim diğeriyle güncellenmeye devam eder.
- GitHub Actions bunu her saat çalıştırır ve fikstür değiştiyse `docs/galatasaray.ics`
  dosyasını günceller; GitHub Pages dosyayı yukarıdaki adresten yayınlar.
- Saati henüz açıklanmamış maçlar o güne "(saat belli değil)" etiketiyle tüm gün etkinliği
  olarak eklenir; saat açıklanınca aynı etkinlik güncellenir.
