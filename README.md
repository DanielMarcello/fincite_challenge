# Fincite Challenge

>Please check the [document](/challenge_document.pdf) for more information

## Installation
1. `git clone` the repository

## Database
1. create a database in `PostgresQL`

### Backend
1. install a virtual environment (`virtualenv`)
1. install `pip`
1. install all dependencies from `requirements.txt`
1. go to `fc` folder
1. create a `.env` file with the variables from de document
1. make migrations for creating the migrations files
1. before running the server run `python manage.py create_initial_data`. this will populate the Locations Model with all South America capitals
1. run `python manage.py runserver 0.0.0.0:8000`

### Frontend
1. go to `frontend` folder
1. run `yarn install`
1. run `yarn start`
