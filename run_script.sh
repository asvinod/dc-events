source venv/bin/activate
pip install -r requirements.txt
python -m  playwright install
python3 update_spreadsheet.py