#!/bin/bash

/usr/sbin/ip addr show tun0 > /dev/null
RETURN_CODE="$?"

if [[ "$RETURN_CODE" -eq 0 ]]; then
    VPN_IP=$(/usr/sbin/ip addr show tun0 | grep inet | awk '{print $2}' | cut -d '/' -f1)
    RTORRENT_IP=$(/usr/bin/ps -ef | sed 's/.*[0-9][0-9]\:[0-9][0-9]\ //g' | grep '^rtorrent' | awk '{print $NF}')
fi

if [[ "$RETURN_CODE" -ne 0 || "$VPN_IP" != "$RTORRENT_IP" ]]
then
	sudo systemctl stop rtorrent*
        RANDOM_CONF=$(basename $(ls /etc/openvpn/*.conf | sort -R | tail -1) .conf)
        sudo systemctl start rtorrent@${RANDOM_CONF}
        echo "Restarted"
else
	echo "Nothing to do"
fi
