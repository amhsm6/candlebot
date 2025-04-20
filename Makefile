SRCS=$(wildcard *.py)

.deploy: $(SRCS)
	comm -addr 192.168.137.56:5000 load $(SRCS)
	touch .deploy

run: .deploy
	comm -addr 192.168.137.56:5000 run

ssh:
	ssh rp@candlebot
