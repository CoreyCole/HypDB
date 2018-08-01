"""Upload Csv Json"""
import json
import falcon

class DownloadCsvJsonResource(object):
  """For downloading csv json files on the client"""
  def on_get(self, req, resp, file_name):
    """Gets the specified csv json file for the client"""
    uploadedJson = json.load(open('./uploads/' + file_name))
    resp.content_type = 'application/json'
    resp.status = falcon.HTTP_200
    resp.body = json.dumps(uploadedJson)
