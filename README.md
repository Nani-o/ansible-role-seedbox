seedbox
=======

This role install a custom seedbox.
Torrents are downloaded via rtorrent which run in a screen, torrents file are uploaded using Dropbox and finally openvpn can be used to download.

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
