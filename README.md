# HBS - Harcama Bilgi Sistemi

Tkinter ile hazırlanmış, SQLite kullanan işletme harcama kayıt ve takip uygulaması.

## Çalıştırma

```bash
python hbs_prototype.py
```

Veriler geliştirme sırasında proje klasöründeki `hbs_data.db` dosyasına yazılır. PyInstaller ile oluşturulan Windows EXE'si verileri `%LOCALAPPDATA%\\HBS\\hbs_data.db` konumunda saklar.

## Windows EXE

GitHub Actions akışı `.github/workflows/build-windows.yml` dosyasındadır. `main` veya `master` dalına gönderim yapıldığında ya da workflow elle çalıştırıldığında `HBS-exe` adlı artifact üretilir.