Test task for 'Betting software' company
=======================================
You can find the task description in the [file](technical-task.pdf)
This is a test task for 'Betting software' company. It is a simple web application that allows to create and manage bets.

There are two apps in the project: 'bet-maker' and 'line-provider'

For starting the project you need to install docker and docker-compose. Then you need to run the following command in the project root directory:

    cp env.example .env
    docker-compose up --build -d
    docker exec betting-line-provider alembic upgrade head
    docker exec betting-bet-maker alembic upgrade head

Bet-maker app will be available on http://0.0.0.0:8000
Line-provider app will be available on http://0.0.0.0:8001

Using redis for queuing. Using postgresql as a database.