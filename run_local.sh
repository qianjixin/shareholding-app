#!/bin/bash

BASEDIR=$(dirname $0)
cd $BASEDIR/src

while :; do python app.py; sleep 5; done
