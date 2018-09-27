"""Test Resource"""
import json
import falcon

class TestResource(object):
  """Experimental endpoint for testing"""
  def on_get(self, req, resp):
    """Experimental endpoint handler for testing"""
    resp.content_type = 'application/json'
    resp.status = falcon.HTTP_200
    resp.body = json.dumps({'hello': 'world'})
