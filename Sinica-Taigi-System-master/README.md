# Sinica Taigi System
1. Taigi Drama transcription correction system
2. Hanzi to Tailo conversion tool
3. Sign to digit for Tailo pinyin conversion tool

## Environment Setup
- joblib
- flask
- Flask-Login
- pymysql
- jieba

## Environment Setup
1. Python packages
  - joblib
  - flask
  - Flask-Login
  - pymysql
  - jieba
2. Firewall (Ubuntu)
  - sudo -S iptables -A INPUT -p tcp --dport <port> -j ACCEPT

## Project Setup
1. Config file
   - prd.py
     - database information
     - user account
     - interface setting
   - playlist.joblib: dramas information (playlist_id, name, product_by, ...)
   - bulletin.py: announcement item
   - changeLog.py: change log item
2. Update correction status for each drama by cronjob
   - Edit the crontable file `crontab -e` and execute update program every X hours
   - e.g. * */4 * * * python update_stat.py
3. Run project
   - firewall: sudo ufw allow <port>/tcp
   - python3 app.py

## Administration
To get the current full list of account and password pair, please contact pinyuan615@gmail.com

  
