# **Finance App**

## **General info**

This Rest API allows the user to track their account balance. \
After creating an account, the user can save customized contracts, savings and recurring savings. \
Then, based on the given current account balance, \
the program will calculate amount that needs to be stored for user's contracts and saving programms, \
as well as the amount disponible after subtracting predicted costs.

**This project is still in progress. [Planning in dropbox paper](https://www.dropbox.com/scl/fi/qvyega08cmrvwa5pu8e5y/Finance-App.paper?dl=0&rlkey=1qa42e9eip31c27e4ih0hh7ys)**

## Table of contents
* [Technologies](#technologies)
* [Setup](#setup)
* [Usage](#usage)
* [Owner](#owner)
* [License](#license)

## **Technologies**

1. Python Django REST Framework
2. PostgreSQL
3. Docker
4. Swagger used for API documentation

------
## **Setup**

### Clone source from git:
```shell
git clone https://github.com/milenakowalska/finance_api
```

### Optional - run python virtual environment:
```shell
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies from requirements.txt:
```shell
pip install -r requirements.txt
```

### Run PostgreSQL and Django App in Docker containers:
```shell
docker compose up
```

The command will run following Docker containers:
1. `financeapp_web_1` - App
2. `financeapp_db_1` - DB

App is running on `http://localhost:8000/`

## Usage

### **Available endpoints:**

1. `/` - GET - documentation of all endpoints
2. `/register` - POST
3. `/login` - POST
4. `/logout` - POST

**Only for logged in users:**

1. `/contracts` - GET - list all user’s contract, POST - create new contract
2. `/contracts/<:id>` - detailed info about specific contract. Available methods: GET, DELETE, PUT
3. `/savings` - GET - list all user’s savings, POST - create new saving
4. `/savings/<:id>` - detailed info about specific saving. Available methods: GET, DELETE, PUT
5. `/recurring-savings` - GET - list all user’s savings, POST - create new recurring saving
6. `/recurring-savings/<:id>` - detailed info about specific recurring saving. Available methods: GET, DELETE, PUT
7. `/statistics` - GET - compute statistics based on account balance
8. `/profile` - GET - info about the user

First you need to create your account using the `/register` endpoint. \
When you log in, you add new contracts and saving programms \
by sending `POST` requests to `/contracts`, `/savings` and `/recurring-savings` endpoints. \
By calling `POST` method on `/statistics` with the account balance in the body, \
you will receive current account statistics -  amount that needs to be stored for your contracts and saving programms, \
as well as the amount disponible after subtracting predicted costs.

## Owner
Created by milenakowalska.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

- **[ Apache 2.0 License ](https://choosealicense.com/licenses/apache-2.0/)**
