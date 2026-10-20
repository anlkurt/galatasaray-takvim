# Galatasaray Süper Lig Takvimi

Galatasaray'ın Trendyol Süper Lig maçlarını Apple Takvim'e (veya herhangi bir takvime)
**abone olunabilir** bir takvim olarak ekler. Maç saatleri açıklandıkça ya da değiştikçe
takvim kendiliğinden güncellenir ve her maçtan **1 saat önce** hatırlatma gelir.

Takvim dosyası: [`docs/galatasaray.ics`](docs/galatasaray.ics)

## Nasıl çalışır?

1. `superlig_takvim.py` TFF'nin resmi haftalık fikstür sayfalarını (1–34. hafta) okur ve
   Galatasaray maçlarını `.ics` dosyasına yazar. TFF'ye ulaşılamazsa ESPN'in fikstür
   verisini yedek olarak kullanır.
2. GitHub Actions (`.github/workflows/takvim.yml`) bunu **her saat** çalıştırır; fikstürde
   bir değişiklik varsa dosyayı günceller.
3. GitHub Pages dosyayı sabit bir adresten yayınlar; Apple Takvim bu adrese abone olup
   düzenli olarak yeniler.

Etkinlikler:
- Saati kesin maçlar 2 saatlik etkinlik olarak eklenir, **1 saat önce** hatırlatma içerir.
- Saati henüz açıklanmamış maçlar o güne **tüm gün** etkinliği olarak
  "(saat belli değil)" etiketiyle eklenir. TFF saati açıklayınca aynı etkinlik saatli hale
  gelir ve hatırlatma eklenir (çift kayıt oluşmaz).
- Oynanmış maçların başlığında skor görünür, ör. `Galatasaray 3-2 Göztepe`.

## Apple Takvim'e ekleme

Takvim adresi: `https://<kullanıcı>.github.io/<repo>/galatasaray.ics`

**Önerilen yol – Mac'ten (iPhone'a iCloud ile gelir):**
1. Takvim → **Dosya → Yeni Takvim Aboneliği…** → adresi yapıştırın → Abone Ol.
2. Açılan pencerede:
   - **Konum:** iCloud (böylece iPhone ve iPad'de de görünür)
   - **Kaldır: Uyarılar** kutusunun işaretini **kaldırın** (işaretli kalırsa 1 saat önceki hatırlatma silinir)
   - **Otomatik yenile:** Her saat
3. Tamam.

**Sadece iPhone'dan:** Ayarlar → Takvim → Hesaplar → Hesap Ekle → Diğer →
*Abone Olunan Takvim Ekle* → adresi yapıştırın. (Bu yolla eklenen takvim yalnızca o
cihazda görünür.)

> Dosyayı tek seferlik içe aktarmayın (import); mutlaka **abone olun**, aksi halde
> saat değişiklikleri gelmez.

## GitHub Actions ücretli mi?

Bu proje için **ücretsiz**:
- **Public** repolarda GitHub Actions'ın standart çalıştırıcıları ücretsiz ve süre sınırsızdır.
- GitHub Pages da public repolarda ücretsizdir.
- (Private repoda Actions ayda 2.000 dakika ücretsiz olurdu ama Pages için ücretli plan
  gerekir; bu yüzden repo public.)

Not: GitHub, 60 gün boyunca hiç commit olmayan public repolarda zamanlanmış iş
akışlarını durdurur (ör. yaz arasında fikstür hiç değişmezse). Böyle olursa GitHub e-posta
atar; repo → **Actions → Takvimi güncelle → Enable workflow** ile tek tıkla tekrar açılır.

## Elle çalıştırma

```bash
python3 superlig_takvim.py
```

Yedek kaynağı zorlamak için:

```bash
python3 superlig_takvim.py --kaynak espn
```

Sadece Python 3 standart kütüphanesi gerekir, ek paket yok. Elle çalıştırmak için de
repo → **Actions → Takvimi güncelle → Run workflow** kullanılabilir.
