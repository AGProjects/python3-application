#!/bin/bash
set -e

distro="${1:-}"

rm -rf dist build

if [ -f setup.py ]; then
    python3 setup.py sdist
else
    python3 -m build --sdist
fi
cd dist

tar zxf *.tar.gz
cd */

# add distro suffix to the changelog version (like autopackager does),
# only in the extracted build tree - never in the source repo
if [ -n "$distro" ] && [ "$distro" != "sid" ]; then
    sed -i "s/) unstable/$distro) $distro/" debian/changelog
    head -1 debian/changelog
fi

debuild --no-sign
