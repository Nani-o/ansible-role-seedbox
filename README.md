[![Build Status](https://travis-ci.org/Nani-o/ansible-role-seedbox.svg?branch=master)](https://travis-ci.org/Nani-o/ansible-role-seedbox)

seedbox
=======

This role installs a custom seedbox.
It allow for torrents and youtube-dl watch folders.
Torrents are downloaded via rtorrent which run in a screen, youtube-dl via a script in crontab.

Requirements
------------

  - CentOS 7

Role Variables
--------------

Variables.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: seedbox }

License
-------

MIT

Author Information
------------------

Sofiane MEDJKOUNE
