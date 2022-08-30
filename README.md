# **Finance App**

## **Technologies**

### Main:
1. Python Django Framework
2. PostgreSQL
3. Docker

### Other:
1. Python static type checker `mypy`

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
