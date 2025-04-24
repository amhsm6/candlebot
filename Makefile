SRCS=$(wildcard *.py)

.deploy: $(SRCS)
	comm -addr 192.168.42.238:5000 load $(SRCS)
	touch .deploy

run: .deploy
	comm -addr 192.168.42.238:5000 run

ssh:
	ssh rp@candlebot
