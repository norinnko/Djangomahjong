# Mahjong Score Calculator (Django, Riichi, Naki supported)

## Setup (Windows PowerShell)

```powershell
cd C:\path\to\mahjong_calc
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Meld input (one per line)
- chi 123m open
- pon 777p open
- kan 9999s closed  (ankan)
- kan 1111m open    (daiminkan)

Hand must be 14 tiles **including meld tiles** (MVP design). We subtract meld tiles internally.
