# Book Catalogue

### [Demo](http://elmadah.pythonanywhere.com)

Requires the following dependencies installed:

* Python 2.7
* Flask
* virtualenv

## Quick Start

### Activate a virtualenv

Install virtualenv on your system.

```sh
$ sudo pip install virtualenv
```
Once you have virtualenv installed, just fire up a shell and create your own environment.

```sh
$ cd IS211_Final/
$ virtualenv ENV
$ . ENV/bin/activate
```

Install the requirements by following command.

```sh
$ pip install -r requirements.txt
```

### Run the Application

```sh
$ python run.py
```
Access the application at the address [http://localhost:5000/](http://localhost:5000/)




### Models (Database)

```sh
$ export FLASK_CONFIG=development
$ export FLASK_APP=run.py
$ flask run
 * Serving Flask app "run"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

1- Create a migration repository
```sh
$ flask db init
```
2- Generate an initial migration
```sh
$ flask db migrate
```
3- Apply the migration to the database
```sh
$ flask db upgrade
```



## Test Users

* Email: admin@example.com
* Password: 123456
* User: Admin
---
* Email: user1@example.com
* Passowrd: 123456
* User: Bill Gates