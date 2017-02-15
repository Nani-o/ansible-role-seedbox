#!/usr/bin/python

import dropbox
import os
import re
import sys
import time
import signal
import sqlite3
import ConfigParser

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

class DropboxWatcher(object):
    """Class for managing some watch folders in Dropbox"""
    def __init__(self, token, watch_folders, watch_folder_path, extensions):
        self.token = token
        self.dbx = dropbox.Dropbox(token)
        self.conn = sqlite3.connect(os.path.join(watch_folder_path, "database.db"))
        self.cur = self.conn.cursor()
        self.watch_folders = watch_folders
        self.watch_folder_path = watch_folder_path
        self.pattern = '(' + '|'.join(['.*' + x + '$' for x in extensions]) + ')'
        self.create_folders()
        self.db_columns = ['date', 'timestamp', 'filename', 'path', 'id', 'rev']
        self.db_init()

    def db_init(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_table = [x[0] for x in self.cur.fetchall()]
        if not "downloads" in available_table:
            self.cur.execute("CREATE TABLE downloads (" + " text, ".join(self.db_columns) + "text)")
        self.conn.commit()

    def db_add_download(self, file):
        values = "(DateTime('now'), strftime('%s', 'now'), '{}', '{}', '{}', '{}')".format(file.name, file.path_display, file.id, file.rev)
        self.cur.execute("INSERT INTO downloads VALUES " + values)
        self.conn.commit()

    def db_search_file(self, id):
        self.cur.execute("SELECT * FROM downloads WHERE id = '{}' order by timestamp desc LIMIT 1".format(id))
        query_result = self.cur.fetchone()
        if query_result:
            result = {}
            for idx, db_column in enumerate(self.db_columns):
                result[db_column] = query_result[idx]
        else:
            result = None

        return result

    def create_folders(self):
        self.dbx_create_folders()
        self.local_create_folders()

    def dbx_create_folders(self):
        folders_present = [x.name for x in self.dbx.files_list_folder('').entries]
        folders_to_create = [x for x in self.watch_folders if x not in folders_present]

        for folder in folders_to_create:
            self.dbx.files_create_folder('/' + folder)

    def local_create_folders(self):
        if not os.path.isdir(self.watch_folder_path):
            print("Le dossier " + self.watch_folder_path + " n'existe pas")
            sys.exit(1)

        for watch_folder in self.watch_folders:
            local_watch_folder = os.path.join(self.watch_folder_path, watch_folder)
            if not os.path.isdir(local_watch_folder):
                os.mkdir(local_watch_folder)

    def dbx_search_files(self):
        files = []
        for folder in self.watch_folders:
            folder_entries = self.dbx.files_list_folder('/' + folder).entries
            files += [x for x in folder_entries if isinstance(x, dropbox.files.FileMetadata) and re.match(self.pattern, x.name)]
        return files

    def local_search_files(self):
        files = []
        for watch_folder in self.watch_folders:
            local_watch_folder = os.path.join(self.watch_folder_path, watch_folder)
            files_list = [{"name": x, "relative_path": os.path.join("/" + watch_folder, x), "path": os.path.join(local_watch_folder, x)} for x in os.listdir(local_watch_folder)]
            files += files_list
        return files

    def sync_files(self):
        dbx_files = self.dbx_search_files()
        local_files = self.local_search_files()
        for file in dbx_files:
            db_entry = self.db_search_file(file.id)
            local_file = os.path.join(self.watch_folder_path, file.path_display.lstrip('/'))
            if not db_entry or db_entry['rev'] != file.rev:
                self.dbx.files_download_to_file(local_file, file.path_lower)
                self.db_add_download(file)
            if db_entry and not os.path.isfile(local_file):
                self.dbx.files_delete(file.path_lower)

        dbx_files_path = [x.path_display for x in dbx_files]
        files_to_remove = [x['path'] for x in local_files if x['relative_path'] not in dbx_files_path]
        for file in files_to_remove:
            os.remove(file)

    def run(self):
        killer = GracefulKiller()
        while True:
            self.sync_files()
            time.sleep(3)
            if killer.kill_now:
                break

script_path = os.path.realpath(__file__)
config_path = os.path.join(os.path.dirname(script_path), os.path.basename(script_path).rstrip('.py') + '.cfg')

config = ConfigParser.RawConfigParser()
config.read(config_path)

token = config.get('global', 'token')
watch_folders = config.get('global', 'watch_folders').split(',')
watch_folder_path = config.get('global', 'watch_folder_path')
extensions = config.get('global', 'extensions').split(',')

dbw = DropboxWatcher(token, watch_folders, watch_folder_path, extensions)
dbw.run()
