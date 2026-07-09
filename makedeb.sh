#!/bin/bash
set -e

rm -rf dist build

if [ -f setup.py ]; then
    python3 setup.py sdist
else
    python3 -m build --sdist
fi
cd dist

tar zxf *.tar.gz
cd */

debuild --no-sign
