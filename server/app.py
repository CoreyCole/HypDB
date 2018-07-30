"""This is the root of the python web server application"""
# python modules
import logging
import json
import falcon
# app middlewares
from middlewares.cors import CORSComponent
# app resources
from resources.test import TestResource

# create info logger
INFO_LOGGER = logging.getLogger('info')
INFO_LOGGER.setLevel(logging.INFO)
# create console handler and set level to info
INFO_CH = logging.StreamHandler()
INFO_CH.setLevel(logging.INFO)
# add INFO_CH to logger
INFO_LOGGER.addHandler(INFO_CH)

# create error logger
ERROR_LOGGER = logging.getLogger('error')
ERROR_LOGGER.setLevel(logging.ERROR)
# create console handler and set level to error
ERROR_CH = logging.StreamHandler()
ERROR_CH.setLevel(logging.ERROR)
# add ERROR_CH to logger
ERROR_LOGGER.addHandler(ERROR_CH)

INFO_LOGGER.info('starting server . . .')

APP = falcon.API(middleware=[
    CORSComponent()
])
# APP.req_options.auto_parse_form_urlencoded = True
APP.add_route('/test', TestResource())
APP.add_route('/api/bias', BiasResource())

INFO_LOGGER.info('started server')
