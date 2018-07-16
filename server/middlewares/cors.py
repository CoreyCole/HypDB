"""This file contains a middleware for allowing cross origin requests"""
class CORSComponent(object):
  """This class is a middleware component for adding the allow CORS header to the response"""
  def process_request(self, req, resp):
    """This adds the CORS header to the response"""
    resp.set_header('Access-Control-Allow-Origin', '*')
    resp.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST')
    resp.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    resp.set_header('Access-Control-Allow-Credentials', True)
