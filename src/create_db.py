#!/usr/bin/env python
# create_db.py
# Mars Target Encyclopedia
# Create the postgresql database.
#
# Kiri Wagstaff
# January 12, 2016

import sys, os

# Import the Python module psycopg2 to enable direct connections to
# the PostgreSQL database.
HAVE_psycopg2 = False
try:
    import psycopg2
    HAVE_psycopg2 = True
except ImportError, e:
    print "The Python module psycopg2 could not be imported, so ",
    print "we cannot access the MTE SQL database."
    sys.exit()

# Connect to the DB
try:
    user = os.environ['USER']
    connection = psycopg2.connect("dbname=mte user=%s" % user)
    cursor     = connection.cursor()

    print 'Checking for existence of MTE databases; '
    print ' will create them if needed.'
    print ' (No output means they already exist.)'

    # If tables don't exist, create them
    # -------- targets -----------
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables " +
                   "WHERE table_name='targets')")
    table_exists = cursor.fetchone()[0]
    if not table_exists:
        print "Creating the targets table from scratch."
        create_table_cmd  = "CREATE TABLE targets ("
        create_table_cmd += " target_id         varchar(100) PRIMARY KEY,"
        create_table_cmd += " target_name       varchar(80),"
        create_table_cmd += " span_start        integer,"
        create_table_cmd += " span_end          integer"
        create_table_cmd += ");"
        cursor.execute(create_table_cmd)

    # -------- components -----------
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables " +
                   "WHERE table_name='components')")
    table_exists = cursor.fetchone()[0]
    if not table_exists:
        print "Creating the components table from scratch."
        create_table_cmd  = "CREATE TABLE components ("
        create_table_cmd += " component_id         varchar(100) PRIMARY KEY,"
        create_table_cmd += " component_name       varchar(80),"
        create_table_cmd += " component_label      varchar(80),"
        create_table_cmd += " span_start           integer,"
        create_table_cmd += " span_end             integer"
        create_table_cmd += ");"
        cursor.execute(create_table_cmd)

    # -------- documents -----------
    DOCUMENTS_TABLE_STATEMENT = '''CREATE TABLE IF NOT EXISTS documents (
        doc_id          VARCHAR(100) PRIMARY KEY,
        title           VARCHAR(1024),
        authors         VARCHAR(4096),
        content         TEXT,
        affiliation     TEXT,
        doc_url         VARCHAR(1024)
    );'''
    cursor.execute(DOCUMENTS_TABLE_STATEMENT)

    # -------- contains -----------
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables " +
                   "WHERE table_name='contains')")
    table_exists = cursor.fetchone()[0]
    if not table_exists:
        print "Creating the contains table from scratch."
        create_table_cmd  = "CREATE TABLE contains ("
        create_table_cmd += " event_id          varchar(100),"
        #create_table_cmd += " doc_id            varchar(100) REFERENCES documents,"
        create_table_cmd += " doc_id            varchar(100),"
        create_table_cmd += " target_id         varchar(100) REFERENCES targets,"
        create_table_cmd += " component_id      varchar(100) REFERENCES components,"
        create_table_cmd += " magnitude         varchar(10),"
        create_table_cmd += " confidence        varchar(10),"
        create_table_cmd += " annotator         varchar(100)"
        create_table_cmd += ");"
        cursor.execute(create_table_cmd)

    # Update permissions
    cursor.execute('grant select, insert, update '
                   'on contains, components, targets, documents '
                   'to youlu, thammegr, wkiri;')
    cursor.execute('grant select '
                   'on contains, components, targets, documents '
                   'to mtedbuser;')

    # Commit changes
    connection.commit()

except psycopg2.Warning, e:
    print 'Warning: ', e
except psycopg2.Error, e:
    print 'Error: ', e
finally:
    cursor.close()
    connection.close()
