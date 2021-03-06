"""
A file for creating the sqlite file with the appropriate schema.
Needs to be run to initialize DB before code review tool can be used.

WARNING:
    Database manipulations in this file are prone to SQL injection.
    It's fine in this case, since it does not take any user input.
    Do not use this code anywhere else without proper modification!
"""

import os
import os.path
import sqlite3
import utils
import argparse
import shutil
from config import *


# A dictionary repr of the schema. Mapping is
# { table_name : { column_name: column_type } }
SCHEMA = {
        'upload': {
            'assign': 'TEXT', #the assignment for which we're looking for the last time
            'last': 'INTEGER' # unix time of last upload
            },
        'roster': {
            'partners': 'TEXT', # login
            'assignment': 'TEXT', # assignment name, eg 'proj4'
            'issue': 'INTEGER' # issue number on rietveld
            },
        }

BACKUP_EXT = ".bkp"

def bkup_if_exists(path):
    """
    Checks if a db already exists. If it does, moves the current
    db to db.bkp.

    Args:
        path: path of sqlite db
    """
    newpath = path + "." + utils.get_timestamp_str() + BACKUP_EXT
    if os.path.exists(newpath):
        raise RuntimeError("Tried to backup the database too fast!") #not sure about this error message
    print('path {}'.format(newpath))
    try:
        # throws OSError if does not exist or is not a file
        os.rename(path, newpath)
        return newpath
    except OSError:
        return None

def create_table(path):
    """
    Call bkup_if_exists before this function.
    Creates tables according to SCHEMA.

    Args:
        path: where the db should be.
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    for table, columns in SCHEMA.items():
        # create list of "col_name col_type"
        columns = ["{0} {1}".format(col_name, col_type) \
                for col_name, col_type in columns.items()]
        # join the list with ","
        columns_str = ",".join(columns)
        # now we can form the SQL string.
        # again, this is NOT sql-injection safe, do not copy-paste
        cursor.execute("CREATE TABLE {0} ({1})".format(table, columns_str))
    conn.commit()
    conn.close()


def import_old_data(db_path, path_to_backup):
    """
    Imports data from the backed up DB into the new one.
    For now, we just want the latest times.
    """
    if not path_to_backup:
        return
    new, old = sqlite3.connect(db_path), sqlite3.connect(path_to_backup)
    new_cursor, old_cursor = new.cursor(), old.cursor()
    all_uploads = old_cursor.execute("SELECT assign, last FROM upload").fetchall()
    insert_query = "INSERT INTO upload (assign, last) VALUES (?, ?)"
    for row in all_uploads:
        new_cursor.execute(insert_query, row)
    all_roster = old_cursor.execute("SELECT partners, assignment, issue FROM roster").fetchall()
    insert_query = "INSERT INTO roster (partners, assignment, issue) VALUES (?, ?, ?)"
    for row in all_roster:
        new_cursor.execute(insert_query, row)
    new.commit()
    old.commit()
    new.close()
    old.close()

def main(transfer, clear, update):
    """
    The main function to run. Populates the database with basic info.
    """
    utils.check_allowed_user()
    db_path = config.DB_PATH
    if transfer or clear:
        backup_path = bkup_if_exists(db_path)
    try:
        if transfer or clear:
            create_table(db_path)
        if transfer:
            import_old_data(db_path, backup_path)
        utils.chown_staff_master(db_path)
        utils.chmod_own_grp_other_read(db_path)
    except Exception as e:
        print("ERROR: {} encountered while initing new database. Restoring old database.".format(e))
        shutil.move(backup_path, db_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initializes the codereview \
                    database, or updates it with new data.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--transfer', action='store_true',
                        help="Creates a new database and transfers the data from the current one (which is now the backup) to the new database.")
    group.add_argument('-c', '--clear', action='store_true',
                        help="Makes a new database which takes none of the old data from the backups.")
    group.add_argument('-u', '--update', action='store_true',
                        help="Updates the current database, while not making a backup.")
    args = parser.parse_args()
    main(args.transfer, args.clear, args.update)
