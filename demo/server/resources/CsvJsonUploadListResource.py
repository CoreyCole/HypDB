"""CsvJsonUploadListResource Resource"""
import fnmatch
import json
import os
import falcon

class CsvJsonUploadListResource(object):
  """CsvJsonUploadListResource"""
  def on_get(self, req, resp):
    """Gets a list of csv json files that have been uploaded"""
    listOfFiles = os.listdir('uploads/')
    pattern = "*.csv.json"
    results = []
    for entry in listOfFiles:  
      if fnmatch.fnmatch(entry, pattern):
        results.append(entry)

    resp.content_type = 'application/json'
    resp.status = falcon.HTTP_200
    resp.body = json.dumps(results)