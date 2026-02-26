psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'icnml_dev' AND pid <> pg_backend_pid();"
psql -c "DROP DATABASE IF EXISTS icnml_dev;"
psql -c "CREATE DATABASE icnml_dev OWNER icnml;"

pg_dump icnml | psql -d icnml_dev

