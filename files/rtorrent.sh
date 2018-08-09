#!/bin/bash

if [[ ! "$1" ]];then
    echo "usage: rtorrent.sh start/stop"
    exit
fi

if [[ "$1" == "start" ]]; then
    for ((i = 0; i < 30; i++))
    do
        sleep 1
        VPN_IP=$(ip addr show tun0 | grep 'inet ' | awk '{print $2}' | sed 's/\/.*//g')
        if [[ "$VPN_IP" != "" ]]
        then
            /usr/bin/screen -dmS rtorrent rtorrent -b "$VPN_IP"
            exit 0
        fi
    done
    echo "tun0 not found"
    exit 1
elif [[ "$1" == "stop" ]]; then
    /usr/bin/screen -S rtorrent -X quit
else
    echo "$1 not recognized\nusage: rtorrent.sh start/stop"
fi
