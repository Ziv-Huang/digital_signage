#!/bin/bash
args1="$1"
rootName=acer
PROJECT_NAME=digital_signage
if [ "$#" -gt 1 ]
then
    exit 1
fi
if [ "$#" -eq 0 ]|| [ $args1 = "--start" ] || [ $args1 = "--restart" ]
then
    # export DISPLAY=:0.0
    # su acer -c "xhost si:localuser:root"
    # xrandr -o normal
    kill $(ps aux | grep $PROJECT_NAME | awk '{print $2}')
    cd $HOME/$PROJECT_NAME
    $HOME/.pyenv/versions/$PROJECT_NAME/bin/python digital_signage.py
elif [ $args1 = "--stop" ]
then
    kill $(ps aux | grep $PROJECT_NAME | awk '{print $2}')
fi