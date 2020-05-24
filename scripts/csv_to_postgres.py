import json
import psycopg2

from datetime import datetime

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


def add_row(cur, table_name, column_names, row):
     cur.execute(('INSERT INTO {} {} VALUES {} ON ' + 
                 'CONFLICT DO NOTHING').format(table_name,
                                               '(' + ', '.join(column_names) + ')',
                                               '(' + ', '.join(row) + ')'))
     return None


print('Psycopg2 connect')
conn = psycopg2.connect('dbname=stanza_dev user=dbuser')
cur = conn.cursor()


print('Load links CSV')
links = pd.read_csv('data/links.csv')


print('Upload links CSV to links table')
lines = links.shape[0]
for i in range(lines):
    if i % 1000 == 0:
        print('{}/{}'.format(i, lines))
    data = [enquote(links.iloc[i].url),
            enquote(links.iloc[i].title),
            enquote(links.iloc[i].summary),
            enquote(links.iloc[i].domain),
            enquote(links.iloc[i].date),
            enquote(links.iloc[i].date),
            str(links.iloc[i].liked),
            enquote(links.iloc[i].category),
            enquote(links.iloc[i].aggregator)]
    add_row(cur,
            'link_link',
            ['url', 'title', 'summary', 'domain', 'added', 'modified', 'liked', 'category', 'aggregator'],
            data)


print('Load upcoming CSV')
upcoming = pd.read_csv('data/upcoming.csv')


print('Upload upcoming CSV to links table')
lines = upcoming.shape[0]
for i in range(lines):
    if i % 1000 == 0:
        print('{}/{}'.format(i, lines))
    data = [enquote(upcoming.iloc[i].url),
            enquote(upcoming.iloc[i].title),
            enquote(upcoming.iloc[i].aggregator),
            enquote('2020-01-01'),
            enquote('2020-01-01')]
    add_row(cur, 'link_link', ['url', 'title', 'aggregator', 'added', 'modified'], data)


conn.commit()
print('Done')
