# Sepal API

## _This project is a WIP_

Sepal is an web app for managing plant collections. For more information see [https://sepal.app](https://sepal.app).

The Sepal API is the driver for the Sepal app. [https://github.com/sepal-app/ui](https://github.com/sepal-app/ui).

## Getting started

The Sepal API requires Python 3.8 or greater.

### Boostrap the database

```sql
CREATE ROLE sepal_user WITH PASSWORD LOGIN 'sepal';
CREATE DATABASE sepal;
ALTER ROLE sepal_user SET client_encoding TO 'utf8';
ALTER ROLE sepal_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sepal_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sepal TO sepal_user;
```

### Require environment variables

```
# The base URL of the Sepal App
APP_BASE_URL=http://localhost:3000

# A postgresql:// url
DATABASE_URL=...

# For building psycopg2 on MacOS if you get an error
LDFLAGS="-L/usr/local/opt/openssl@1.1/lib"
CPPFLAGS="-I/usr/local/opt/openssl@1.1/include"

# For sending email
MAILGUN_API_KEY=...
MAILGUN_API_URL=...

# The Firebase project id.  Firebase is used for authentication.
FIREBASE_PROJECT_ID=sepal-development

# You can either set GOOGLE_APPLICATION_CREDENTIALS to point to a the JSON credentials file to the Google Cloud service account or set GOOGLE_APPLICATION_CREDENTIALS_JSON to a string containing the JSON.  It's not necessary to set both.
# export GOOGLE_APPLICATION_CREDENTIALS=firebase-adminsdk-credentials.json
export GOOGLE_APPLICATION_CREDENTIALS_JSON=`cat firebase-adminsdk-credentials.json`
```

### Create the Python virtual environment

```
make venv
```

### Apply database migrations

```
make db:upgrade
```

### Start the server

```
make server:start
```

### Autogenerate a new database migration

```
make db:migrate
```

### Run tests

```
make tests
```
