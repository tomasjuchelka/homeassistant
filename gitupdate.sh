#!/bin/sh

sudo chown -R pi:pi .
git secret hide -m
git add .
git status

echo -n "Enter the Description for the Change: "
read CHANGE_MSG

git commit -m "${CHANGE_MSG}"
exit