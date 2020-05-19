# Coffee Shop Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=api.py
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Tasks

### Setup Auth0

1. Create a new Auth0 Account
2. Select a unique tenant domain
3. Create a new, single page web application
4. Create a new API
    - in API Settings:
        - Enable RBAC
        - Enable Add Permissions in the Access Token
5. Create new API permissions:
    - `get:drinks-detail`
    - `post:drinks`
    - `patch:drinks`
    - `delete:drinks`
6. Create new roles for:
    - Barista
        - can `get:drinks-detail`
    - Manager
        - can perform all actions
7. Test your endpoints with [Postman](https://getpostman.com). 
    - Register 2 users - assign the Barista role to one and Manager role to the other.
    - Sign into each account and make note of the JWT.
    - Import the postman collection `./starter_code/backend/udacity-fsnd-udaspicelatte.postman_collection.json`
    - Right-clicking the collection folder for barista and manager, navigate to the authorization tab, and including the JWT in the token field (you should have noted these JWTs).
    - Run the collection and correct any errors.
    - Export the collection overwriting the one we've included so that we have your proper JWTs during review!

https://antal.eu.auth0.com/authorize?audience=coffeeshopudacity&response_type=token&client_id=zs7wnlYexq8KUS50udXkQHyDIoFWCHvy&redirect_uri=http://localhost:8080

toniquez@gmail.com
access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZFNS1JaEF3MTREdXQ1WkxPcnZJUCJ9.eyJpc3MiOiJodHRwczovL2FudGFsLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZWI5OTUwOWE1ZmE0YTBiZWY3MDk2MmEiLCJhdWQiOiJjb2ZmZWVzaG9wdWRhY2l0eSIsImlhdCI6MTU4OTIyMjQ1OSwiZXhwIjoxNTg5MjI5NjU5LCJhenAiOiJ6czd3bmxZZXhxOEtVUzUwdWRYa1FIeURJb0ZXQ0h2eSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlIiwiZ2V0IiwicGF0Y2giLCJwb3N0Il19.W9PnIySVKpt2ZynvB9gy5pdD87C4WtiYSi5zHGBOKbbOfVik5sJzEl2fyimb380qyo2YNSLJXNbHB877CdR_58HfdiiRzpzxmQmgyfpguE7Ti8m6r8iiS-OXDsxkj_1pxbF3vx4eoRMuTesgKYyr7hQ0UG0Z8Glqg-mvah_k3z50cSKjyJEbxm-xNtLykBsJyaVZAAiZzYv7gEigZeLeHS9L8cFMVOVJsMHRe0FFdSfwDnuoSaS7n6f-tLwWp1frXJJ005FKXWEKBeDMB076QZIPhUeDMdHh3U09Q1-wUAFHLHXAgTXRyyAKVJULqv7xGl5tvS1sKQsSTqjsouPEpA&expires_in=7200&token_type=Bearer

a.tettinger@yahoo.com
ccess_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InZFNS1JaEF3MTREdXQ1WkxPcnZJUCJ9.eyJpc3MiOiJodHRwczovL2FudGFsLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZWI5OTViZmE1ZmE0YTBiZWY3MDk2ZDAiLCJhdWQiOiJjb2ZmZWVzaG9wdWRhY2l0eSIsImlhdCI6MTU4OTIyMjUyMywiZXhwIjoxNTg5MjI5NzIzLCJhenAiOiJ6czd3bmxZZXhxOEtVUzUwdWRYa1FIeURJb0ZXQ0h2eSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0Il19.WcPKgbJcq_ZIcQ5rsK3oqg0n6ke95jgnguMpaus5UBe2VpEm8k8AB7QALoM06lEmIGJwsNQ9Nqce44WYsWaLYltWMwTjvyDVhvH6dpdA8BAfip190VieBJDI8aosaqBVdw9sJx4SfY3xUAIMvbQiRGGBcu26BBeK4Jp-ZhovruJBccwvi3dreHNIoNSve8pMt-uZD317NKNuxFtGZQR-WykgLHVEH3YwuThiBwP-Z1PNDzVhlxw21qBRtEUCd2iGG0kj62ZZtmAX-jDvqYUT8LplCV2GXqF9AH1lrpPvgYEo6fr4YNtpGpXqeAoXogNLEcU2rsM3ow01n9P9k_PNOQ&expires_in=7200&token_type=Bearer

### Implement The Server

There are `@TODO` comments throughout the `./backend/src`. We recommend tackling the files in order and from top to bottom:

1. `./src/auth/auth.py`
2. `./src/api.py`