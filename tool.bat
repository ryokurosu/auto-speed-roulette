git pull origin master
cd wenv/Scripts
call activate.bat
cd ..
cd ..
pip install -r requirements.txt
start python cron.py