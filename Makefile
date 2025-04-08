SRCS=$(wildcard *.py)

.deploy: $(SRCS)
	comm load $(SRCS)
	touch .deploy

run: .deploy
	comm run

ssh:
	ssh rp@candlebot
