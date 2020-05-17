import json
import psycopg2
import pandas as pd


def table_exists(cur, table_name):
    cur.execute('SELECT * FROM information_schema.tables WHERE table_name=%s', (table_name,))
    return cur.rowcount >= 1


def drop_table(cur, table_name):
    cur.execute('DROP TABLE {}'.format(table_name))
    return None


def escape(text):
    return text.replace('\'', '\'\'')

def enquote(text):
     return '\'' + escape(str(text)) + '\''


def add_row(cur, table_name, row):
     cur.execute('INSERT INTO {} VALUES {}'.format(table_name, '(' + ', '.join(row) + ')'))
     return None


def create_links_table(cur):
     # TODO: Use Django migration
    cur.execute("""
        CREATE TABLE links(
            id integer PRIMARY KEY,
            url text,
            title text,
            summary text,
            domain text,
            date timestamp,
            liked integer,
            category text,
            aggregator text
        )
    """)
    return None


def create_upcoming_table(cur):
     # TODO: Use Django migration
    cur.execute("""
        CREATE TABLE upcoming(
            id integer PRIMARY KEY,
            url text,
            title text,
            aggregator text
        )
    """)
    return None

print('Psycopg2 connect')
conn = psycopg2.connect('dbname=stanza_dev user=dbuser')
cur = conn.cursor()


# TODO: Use Django migration
print('Check links table')
if table_exists(cur, 'links'):
    print('Drop existing links table')
    drop_table(cur, 'links')

print('Create empty links table')
create_links_table(cur)
conn.commit()


print('Load links CSV')
links = pd.read_csv('data/links.csv')


print('Upload links CSV to links table')
lines = links.shape[0]
for i in range(lines):
    if i % 1000 == 0:
        print('{}/{}'.format(i, lines))
    data = [enquote(i),
             enquote(links.iloc[i].url),
            enquote(links.iloc[i].title),
            enquote(links.iloc[i].summary),
            enquote(links.iloc[i].domain),
            enquote(links.iloc[i].date),
            str(links.iloc[i].liked),
            enquote(links.iloc[i].category),
            enquote(links.iloc[i].aggregator)]
    add_row(cur, 'links', data)


# TODO: Use Django migration
print('Check upcoming table')
if table_exists(cur, 'upcoming'):
    print('Drop existing upcoming table')
    drop_table(cur, 'upcoming')

print('Create empty upcoming table')
create_upcoming_table(cur)
conn.commit()


print('Load upcoming CSV')
upcoming = pd.read_csv('data/upcoming.csv')


print('Upload upcoming CSV to upcoming table')
lines = upcoming.shape[0]
for i in range(lines):
    if i % 1000 == 0:
        print('{}/{}'.format(i, lines))
    data = [enquote(i),
            enquote(upcoming.iloc[i].url),
            enquote(upcoming.iloc[i].title),
            enquote(upcoming.iloc[i].aggregator)]
    add_row(cur, 'upcoming', data)


print('Done')
