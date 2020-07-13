## Boostrap the database

```sql
CREATE ROLE sepal_user WITH PASSWORD LOGIN 'sepal';
CREATE DATABASE sepal;
ALTER ROLE sepal_user SET client_encoding TO 'utf8';
ALTER ROLE sepal_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sepal_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sepal TO sepal_user;
```
