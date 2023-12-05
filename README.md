# Read Meross Smart Plug values and exposes them via HTTP

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://github.com/luisgs/)

MerosStats script is based on this famous Meross-iot package [here] and more precisly in this script here.

MerosStats script logins, finds and reads a SINGLE Meross Smart Plug with readable energy capabilities AND exposes it via HTTP.

Exposed HTTP page with energy values is ready for monitoring tools like Prometheus so they can read into it.

## Tech

MerosStats uses these technologies:

- Python
- Meross-iot
- Prometheus Client [Gauge, start_http_server]

## Requirements

We recomend to create a venv where you can install required packages:
    pip install -r requirements.txt

## Use

Firstly, create ENV variables or modify head of the script with Meross USER and EMAIL values.

How to execute this script:

```sh
[sudo] python3 meross_stats.py
```

## Docker

MerosStat script can be deployed as docker.

You can find a dockerfile in here

This repository includes a Dockerfile with all required info.

```sh
[sudo] docker build --no-cache -t meross .
```

How to run it:
```sh
[sudo] docker run --rm meross
```
OR
```sh
[sudo] docker run --rm -e EMAIL=email.com -e PASSWORD=password 0.0.0.0:8040:8000 meross
```

