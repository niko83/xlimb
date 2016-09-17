kill `ps -ef | grep server.py | grep -v grep | awk '{ print $2 }'`;
kill `ps -ef | grep start_bot.py | grep -v grep | awk '{ print $2 }'`;

nohup /home/ship/venv/bin/python /home/ship/app/src/server.py 8080 &
sleep 3
nohup /home/ship/venv/bin/python /home/ship/app/src/start_bot.py 5 &
