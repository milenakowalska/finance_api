# **Finance App**

[Planning in dropbox paper](https://www.dropbox.com/scl/fi/qvyega08cmrvwa5pu8e5y/Finance-App.paper?dl=0&rlkey=1qa42e9eip31c27e4ih0hh7ys)
## **Technologies**

1. Python Django Framework
2. PostgreSQL
3. Docker
4. Swagger used for API documentation

------
## **Local checkout and first run**

### Clone source from git
`git clone https://github.com/milenakowalska/finance_api`

### Optional - run python virtual environment
`python3 -m venv venv`
`source venv/bin/activate`

### Install dependencies from requirements.txt
`pip install -r requirements.txt`

### Run PostgreSQL and Django App in Docker containers:
`docker compose up`


1. `financeapp_web_1` - App
2. `financeapp_db_1` - DB

App is running on `http://localhost:8000/`
