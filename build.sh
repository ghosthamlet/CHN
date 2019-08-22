#!/bin/bash

rm -rf build dist

pyinstaller ui.spec

cp -r ~/.local/lib/python3.6/site-packages/en_core_web_sm/ dist/CHN/
cp -r ~/.local/lib/python3.6/site-packages/en_core_web_md/ dist/CHN/

cd dist/CHN/ 
./CHN
