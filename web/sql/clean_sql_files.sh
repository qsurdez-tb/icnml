#!/bin/bash

find . -name '*.sql' -exec sed -i -e '/^--/d' -e '/^$/N;/^\n$/D' -e 's/OWNER TO postgres;/OWNER TO icnml;/g' {} \;

