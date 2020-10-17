#!/bin/sh

git secret hide
git add .
git status

echo -n "Enter the Description for the Change: " [Minor Update]
read CHANGE_MSG

git commit -m "${CHANGE_MSG}"
exit
