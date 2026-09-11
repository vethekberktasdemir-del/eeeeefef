# HBS 2.0 - Harcama Bilgi Sistemi (Advanced)

Tkinter, SQLite ve Matplotlib ile hazırlanmış, gelişmiş özellikler içeren işletme harcama kayıt ve takip uygulaması.

## ✨ Yeni Özellikler (v2.0)

### 📊 Grafik ve İstatistikler
- **Günlük Harcama Trendi** - Line chart ile harcama akışını görüntüle
- **Kategoriye Göre Dağılım** - Pie chart ile kategori analizleri
- **Ödeme Yöntemine Göre Analiz** - Bar chart ile ödeme metodlarını karşılaştır
- **Aylık Harcama Toplamı** - Aylık karşılaştırma grafikleri
- **Dinamik Dönem Seçimi** - Bu Ay, Son 3 Ay, Son 6 Ay, Tüm Veriler

### 💰 Gelir Takibi
- Gelir kaydı ekleme, düzenleme, silme
- Gelir kaynağı ve tarihi kaydı
- Gelir CSV aktarımı
- Toplam gelir kartı

### 🎯 Bütçe Yönetimi
- Kategorilere bütçe limiti ayarlama
- Harcanan vs Kalan bütçe karşılaştırması
- Bütçeyi aşan harcamaları ⚠️ uyarı ile gösterme
- Aylık bütçe planlaması

### 📋 Raporlama
- Tarih aralığına göre rapor oluşturma
- Kategoriye göre detaylı analiz
- Yüzde hesaplaması
- Özet ve detaylı rapor görüntüleme

### 📊 Dashboard
- Toplam Harcama kartı
- Toplam Gelir kartı
- Net Kar/Zarar kartı
- Bu Ay Harcama kartı
- Gerçek zamanlı güncelleme

## 🎨 Sekme Yapısı

1. **📊 Dashboard** - Özet istatistikler ve KPI'lar
2. **💸 Harcama Yönetimi** - Harcama ekle, düzenle, sil, ara
3. **💰 Gelir Yönetimi** - Gelir ekle, düzenle, sil, ara
4. **📈 Grafik & İstatistikler** - Dinamik grafikler ve analiz
5. **🎯 Bütçe Yönetimi** - Bütçe limitleri ve takibi
6. **📋 Raporlama** - Detaylı raporlar ve dışa aktarım

## 📦 Kurulum

```bash
# Gerekli paketler
pip install matplotlib

# Çalıştırma
python hbs_advanced.py
```

## 💾 Veri Saklama

- **Geliştirme:** `hbs_data.db` (proje klasöründe)
- **Windows EXE:** `%LOCALAPPDATA%\HBS\hbs_data.db`

## 📊 Veritabanı Tabloları

- **expenses** - Harcama kayıtları
- **income** - Gelir kayıtları
- **budgets** - Bütçe limitleri
- **categories** - Harcama kategorileri

## 🎨 Renkler

- **Ana Renk:** #118C4F (Yeşil)
- **Başarı:** #10B981 (Açık Yeşil)
- **Uyarı:** #F59E0B (Sarı)
- **Hata:** #EF4444 (Kırmızı)
- **Bilgi:** #3B82F6 (Mavi)

## 📝 Özellikleri

✅ Harcama ekle/düzenle/sil
✅ Gelir ekle/düzenle/sil
✅ Bütçe yönetimi
✅ Grafik ve İstatistikler
✅ Raporlama
✅ CSV aktarım
✅ Arama ve filtreleme
✅ Türkçe dil desteği

## 🚀 Geliştirme Ortamı

- Python 3.8+
- Tkinter (dahil)
- SQLite3 (dahil)
- Matplotlib 3.5+

## 📄 Lisans

Kamacıoğlu Et Entegre tarafından geliştirilmiştir.
Veteriner Hekim Berk Can TAŞDEMİR

---

**Sürüm:** 2.0 Advanced
**Son Güncelleme:** 2026-09-11
