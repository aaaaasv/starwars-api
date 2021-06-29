# StarWars API

## General info

A backend API for fetching Star Wars characters info from [SWAPI](https://github.com/phalt/swapi), storing it, and retrieving with a possibility to do some exploratory operations on it.

## Built with

* [Python 3.8](https://www.python.org/)
* [FastAPI 0.65.2](https://fastapi.tiangolo.com/)

## Setup

1. Clone the repository:

```sh
$ git clone https://github.com/aaaaasv/starwars-api.git
$ cd starwars-api
```

2. Create virtual environment:

```sh
$ python -m venv venv
$ source venv/bin/activate
```

3. Install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```

4. Once `pip` has finished downloading the dependencies run the server:

```sh
(venv)$ uvicorn core.main:app --reload
```
And navigate to `http://127.0.0.1:8000`.

Default database is SQLite, but the application has also been tested with [PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html).
## Usage

On the `/docs` or `/redoc` pages, you can find  API documentation.

Application relies on external [API](https://swapi.co/api/people/), if it is not accessible, you should host your [own version](https://github.com/phalt/swapi) of it for everything to work.

### Authentication

Application supports JSON Web Tokens:
* `users/token` - to obtain a new token

### Tests

```
(venv)$ pytest
```