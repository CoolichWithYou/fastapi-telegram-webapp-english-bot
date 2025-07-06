webapp_run:
	sudo docker compose up --build

db:
	sudo ENV_FILE=.env.dev docker compose up --build -d db
	cd bot && python main.py

dev:
	tmux new-session -d -s myapp 'cd server && python pdb main.py' \; \
	split-window -h 'cd bot && python pdb main.py' \; \
	attach-session -t myapp

prod:
	sudo ENV_FILE=.env.prod docker compose up --build
