import pandas as pd
import psycopg2

def read_from_csv(filename, sep=None, header=0, to_drop=None):
    """
    Load data from csv into a FairDB friendly format
    Parameters:
    -----------
    filename :
        abs path of the csv
    sep :
        data separator (regex or string)
    header :
        number of header lines to drop
    to_drop : opt
        A list with attributes (columns) to drop from the loaded data
    Returns
    -------
    data :
        the loaded dataset
    """
    try:
        if sep:
            _sep = sep
        else:
            _sep = r'\s*,\s*'

        data = pd.read_csv(filename, header=header, sep=_sep, engine='python',
                           na_values="?")

        if to_drop:
            for attribute in to_drop:
                data = data.drop(attribute, axis=1)

    except IOError:
        print("Error: Cannot open file \"%s\"" % filename)
        raise
    except Exception as inst:
        print("Error: {} loading data from file {}".format(inst, filename))
        raise

    return data


def read_from_db(relation, condition=None,host='localhost', user='bsalimi', password='1', dbname='postgres'):
    Connection = psycopg2.connect(host=host, user=user, password=password, dbname=dbname)
    try:
        if condition == None:
            query = 'SELECT * FROM {}'.format(relation)
        else:
            query = 'SELECT * FROM {} where {}'.format(relation, condition)
        df = pd.read_sql_query(query, con=Connection)
    except Exception as inst:
        print("Error: {} loading data from database {}".format(inst, relation))
        raise
    return df