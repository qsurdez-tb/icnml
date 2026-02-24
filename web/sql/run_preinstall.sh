sudo -u postgres psql -d postgres -a -f ./preinstall/00-database.sql
sudo -u postgres psql -d postgres -a -f ./preinstall/00-roles.sql
