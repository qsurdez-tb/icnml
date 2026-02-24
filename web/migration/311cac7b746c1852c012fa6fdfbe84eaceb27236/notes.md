# What

This folder documents the changes related to the database for the commit 311cac7b746c1852c012fa6fdfbe84eaceb27236.
This commit was done to merge the `refactoring/cnm` branch in the `develop` one, changing the way to store the close non match and afis searches in the database.

# Before starting

First, read the `web/app/migration/311cac7b746c1852c012fa6fdfbe84eaceb27236/migration.py` python file.

The `db_url_in` and `db_url_out` variables shall be updated correctly to point to the correct database (probably the same one for the production database).

It is recommended to test the migration process on a backup of the database.

# Migration process

First, rename all the old tables staring with `cnm_` to `cnm_..._old`.
The `migration.py` script will assume all old tables have the correct name with `_old` at the end.

Then, run the `web/app/migration/311cac7b746c1852c012fa6fdfbe84eaceb27236/tables.sql` script to create all the new tables correctly.

The `web/app/migration/311cac7b746c1852c012fa6fdfbe84eaceb27236/migration.py` file is used to copy the data from the old format to the new one.

# After

Once the migration is done, restart the web containers with the new version (branch merged in develop).

