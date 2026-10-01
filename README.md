# HBS - Harcama Bilgi Sistemi

Tkinter ile hazırlanmış, SQLite kullanan işletme harcama kayıt ve takip uygulaması.

## Çalıştırma

```bash
python -m pip install matplotlib
python "HARCAMA DETAYLI.py"
```

Windows'ta kaynak dosyayı konsol penceresi açmadan çalıştırmak için `pythonw "HARCAMA DETAYLI.py"` kullanın. Veriler geliştirme sırasında proje klasöründeki `hbs_data.db` dosyasına yazılır. PyInstaller ile oluşturulan Windows EXE'si verileri `%LOCALAPPDATA%\\HBS\\hbs_data.db` konumunda saklar.

## Windows EXE

GitHub Actions akışı `.github/workflows/build-windows.yml` dosyasındadır. `main` veya `master` dalına gönderim yapıldığında ya da workflow elle çalıştırıldığında, konsol penceresi açmayan `HBS-exe` artifact'i `HARCAMA DETAYLI.py` kaynağından üretilir.