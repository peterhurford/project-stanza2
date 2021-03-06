import io
import re
import csv

import pandas as pd


ALL_COLS = ['id', 'url', 'title', 'summary', 'domain', 'added', 'modified',
            'liked', 'category', 'aggregator', 'seed']


def table_exists(cur, table_name):
    cur.execute('SELECT * FROM information_schema.tables WHERE table_name=%s', (table_name,))
    return cur.rowcount >= 1


def drop_table(cur, table_name):
    cur.execute('DROP TABLE {}'.format(table_name))
    return None


def escape(text, quote='\''):
    return text.replace(quote, '\{}'.format(quote))

def enquote(text, quote='\''):
     return quote + escape(str(text), quote=quote) + quote


def add_row(cur, table_name, column_names, row):
     cur.execute('INSERT INTO {} {} VALUES {}'.format(table_name,
                                                      '(' + ', '.join(column_names) + ')',
                                                      '(' + ', '.join(row) + ')'))
     return None


def delete_row(cur, table_name, column_name, value):
    cur.execute('DELETE FROM {} WHERE {} = {}'.format(table_name, column_name, value))
    return None


def update_row(cur, table_name, set_col, set_val, where_col, where_val):
    cur.execute('UPDATE {} SET {} = {} WHERE {} = {}'.format(table_name,
                                                             set_col,
                                                             set_val,
                                                             where_col,
                                                             where_val))
    return None


def find_row(cur, table_name, col, value, n=1):
    cur.execute('SELECT * FROM {} WHERE {} = {}'.format(table_name, col, enquote(value)))
    if n == 1:
        return cur.fetchone()
    elif n == 'many':
        return cur.fetchall()
    else:
        return ValueError('n must be 1 or many')


def export_db(cur, outfile='data/export.csv', verbose=True):
    with open(outfile, 'w') as f:
        if verbose:
            print('...Downloading')

        # Ideally we would just copy directly, but Heroku permissions don't allow that
        # so we have to hack around with StringIO 
        data_io = io.StringIO()
        cur.copy_to(data_io, 'link_link', sep=',')
        data_io.seek(0)
        content = data_io.read()
        if content == '':
            blank_db = True
        else:
            blank_db = False
            content = content.split('\n')
            # Use re.split to ignore escaped commas
            content = [re.split('(?<!\\\\),', c) for c in content]
            writer = csv.writer(f, delimiter=',')
            writer.writerows(content)

    if verbose:
        print('...Formatting')

    if blank_db:
        links = None
    else:
        links = pd.read_csv(outfile, header=None)
        links.columns = ALL_COLS
        links = links[links['id'].notnull()]   # Drop empty column
        links['id'] = links['id'].astype(int)  # Fix float ID issue
        links = links.sort_values('id')
        links.to_csv(outfile, index=False)

    return links


def import_db(conn, infile='data/export.csv', verbose=True):
    data_io = io.StringIO()
    df = pd.read_csv(infile)
    df.to_csv(data_io, index_label='id', header=False, index=False)
    data_io.seek(0)
    cur = conn.cursor()
    if verbose:
        print('...Clearing table')
    cur.execute('DELETE FROM link_link')
    if verbose:
        print('...Importing to PSQL')
    cur.copy_from(data_io, 'link_link', sep=',')
    conn.commit()
    cur.close()
    return None

