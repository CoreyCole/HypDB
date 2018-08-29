import warnings
warnings.filterwarnings("ignore")

import reprlib
import pprint

import pandas as pd

"""
Bias Resource

Computes bias statistics
"""
import csv
import json
import falcon

# HypDB imports
from os import chdir
from FairDB.core.cov_selection import FairDB
from FairDB.core.explanation import top_k_explanation
import FairDB.core.query as sql
from FairDB.core.matching import *
import time
import FairDB.core.simdetec as simp
from FairDB.utils.util import bining, get_distinct
from Bias import BiasResource
import FairDB.modules.statistics.cit as test


class BiasAteResource(object):
    """Resource for computing bias statistics"""

    def on_post(self, req, resp):
        """endpoint for returning naive group by query results"""
        # Process request
        params = json.load(req.bounded_stream)
        # print(json.dumps(params))
        filename = params['filename']
        # Create data
        data = read_from_csv('./tmp/' + filename)
        # print('data size: ', len(data))

        # Processwhere clause
        # TODO: need support for multiple where statements separated by or
        # TODO: support in clause
        # data = data[data['carrier'].isin(['AA', 'UA'])]
        # data = data[data['origin'].isin(['COS', 'MFE', 'MTJ', 'ROC'])]
        # print(len(data))

        if 'where' in params and params['where'] != 'undefined':
            #print(len(data))
            #data = data.query("carrier in ('UA', 'AA') and origin in ('COS', 'MFE', 'MTJ', 'ROC') and carrier != 'UA'")
            #print(len(data))
            key = next(iter(params['where']))
            data = BiasResource.parseWhere(key, params['where'][key], data)
            # print('data size (post where clause): ', len(data))
        if len(data) == 0:
            raise ValueError('No rows remaining in database after where clause')
            #if params['where']:
            #    # change = to ==
            #    addEquals = params['where'].split('=', 1)
            #    data = data.query(addEquals[0] + '==' + addEquals[1])

        # Process group by
        treatment = []
        if 'groupingAttributes' in params:
            if params['groupingAttributes']:
                for attr in params['groupingAttributes']:
                    treatment.append(attr)

        # Process select
        outcome = [params['outcome']]

        # Naive group-by query, followd by a conditional independance test
        ate = sql.naive_groupby(data, treatment, outcome)
        ate_data = sql.plot(ate, treatment, outcome)

        pvalue = 0.01
        debug = False
        loc_num_samples = 1000
        num_samples = 1000

        low, high, I = test.ulti_fast_permutation_tst(data, treatment, outcome, pvalue=pvalue,
                                                  debug=debug,loc_num_samples=loc_num_samples,
                                                  num_samples=num_samples,view=False)

        low = '%.3f' % (low) if low else 0
        high = '%.3f' % (high) if high else 0
        I = '%.6f' % (I) if I else 0

        outJSON = {
            'low' : low,
            'high' : high,
            'cmi' : I,
            'naiveAte': ate_data,
            'graph': {
                'correlation': {
                    'outcome': [outcome],
                    'treatment': [treatment]
                }
            }
        }

        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(outJSON)
        return resp