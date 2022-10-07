# Docker Italy dashboard
Italy docker image for [Covid-Dashboard](https://github.com/alex27riva/Covid-dashboard) thesis project.

## Building
`docker build -t alex27riva/dash_italy:latest .`

## Run
`docker run --restart=always --name dashboard_italy -d -p 8050:8050 alex27riva/dash_italy`