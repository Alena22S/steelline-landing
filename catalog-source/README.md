# Перенос со старого сайта и сборка

Скрипты и данные переноса со steelline.store (Tilda) и aurum-doors.store. На сервер не выкладываются
(`catalog-source/` исключена в `.github/workflows/deploy.yml`). Большие сохранённые страницы старых сайтов
(`sl-html/`, `aurum/html/`) в репозиторий не кладутся — при необходимости скачиваются заново (`sl_crawl.py`, `aurum/crawl.py`).

| Скрипт | Что делает |
|---|---|
| `merge_specs.py` | характеристики, панели, серии и признак «с терморазрывом» входных дверей → `prototype-catalog/data/catalog.json` |
| `aurum/crawl.py`, `aurum/parse.py`, `aurum/to_catalog.py` | межкомнатные двери Aurum → `prototype-catalog/data/aurum.json` + фото |
| `stores.py` | «Наши магазины» → `prototype-catalog/data/stores.json` + фото салонов |
| `gid.py` | «Гид по продукту»: видео Rutube и технологии отделки → `prototype-catalog/data/gid.json` |
| `designers.py` | «Дизайнерам и архитекторам»: фото, вырезанные из слайдов презентации |
| `redirects.py` | таблица 301-переадресаций старых адресов → `redirects.csv` и `server/nginx-steelline.conf` |
| `migrate.py` | переезд на домен: `python3 catalog-source/migrate.py https://steelline.store` |

Страницы сайта собирает `prototype-catalog/build.py` (запускать после любых правок `index.html` и данных).
Скриптам с фото нужен Python с Pillow и BeautifulSoup (`pip install pillow beautifulsoup4`).
