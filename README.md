# Oyun Deneme

## Genel Bakış
- Basit bir tower defense oyunu; modüler mimari ile yazıldı.
- Event/Observer, Strategy ve Factory desenleri kullanır.
- Tek dosya `.exe` veya Python ile kaynak koddan çalıştırılabilir.

## Özellikler
- Event tabanlı giriş ve UI yönetimi (`core/events.py`).
- Hedef seçimi için strateji sınıfları (`gameplay/strategy.py`).
- Varlık üretimi için factory (`engine/factory.py`).
- Basit object pool ile mermi yönetimi (`engine/pool.py`).
- Modernize edilmiş UI elementleri (`ui/elements.py`).

## Çalıştırma
- Tek dosya exe ile:
  - PowerShell: `& "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme\OyunDeneme.exe"`
  - Klasöre giderek: `cd "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme"` ardından `.\nOyunDeneme.exe`
- Kaynak koddan (Python 3.12+ önerilir):
  - `python "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme\game.py"`

## Paketleme (PyInstaller)
- Tek dosya exe üretmek:
  - `pyinstaller --noconfirm --clean --onefile --name OyunDeneme "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme\game.py" --add-data "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme\assets;assets" --add-data "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme\settings.json;."`
- Konsol penceresini gizlemek için `--windowed` ekleyebilirsin.
- Derleme artıkları (`build`, `dist`, `*.spec`) oyun çalışması için gerekli değildir; isteğe bağlı temizlenebilir.

## Yapı
- `assets/` oyun görselleri ve sesler
- `core/` çekirdek event ve logging, config loader
- `engine/` render, transitions, upgrades, factory/pool
- `gameplay/` towers/enemies/bullets, strategy
- `systems/` input/sound/score
- `ui/` hud/menu/overlays/settings/upgrade, UIElement tabanı
- `game.py` oyun motoru ve ana döngü
- `settings.json` kullanıcı ayarları

## Ayarlar (`settings.json`)
- `music_volume`: `0.0`–`1.0`
- `sfx_volume`: `0.0`–`1.0`
- `fullscreen`: `true/false`
- `show_fps`: `true/false`
- `difficulty`: `easy|normal|hard`
- `controls`: ileri kullanım için rezerv; sözlük olmalı

## Kontroller
- `Space`: Manuel ateş
- `U`: Upgrade panelini aç/kapat
- `Q`: Ulti kullan
- `Esc`: Pause/Continue
- `1/2/3`: Upgrade kısayolları (range/firerate/bullet)
- Debug (isteğe bağlı): `F1,F2,F3,F4,F5,F6,F7,F8,F9,F10`, `Tab`, `Ctrl+S`

## Sorun Giderme
- Boşluk içeren yolu komut satırında çalıştırırken tırnak ve çağrı operatörü kullan:
  - `& "C:\Users\BATIN\Desktop\oyun denemesi\oyun_deneme\OyunDeneme.exe"`
- Exe’de asset/ayar yükleme: kod `sys._MEIPASS` ile paket yolu destekler.
- `Event` hatası: UI modüllerinde `Event` ve sabitler modül başında import edilir.

## Lisans ve Asset Notları
- Asset dosyaları telif durumuna göre lisanslanmalıdır; harici paylaşımda uygun lisansı ekle.

