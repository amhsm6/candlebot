SRCS=$(wildcard *.py)

.deploy: $(SRCS)
	scp -r $(SRCS) rp@candlebot:~/src/root
	touch .deploy

run: .deploy
	ssh -t rp@candlebot sudo python /home/rp/src/root/main.py

ssh:
	ssh rp@candlebot
