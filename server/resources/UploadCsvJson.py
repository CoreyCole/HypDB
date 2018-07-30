"""Upload Csv Json"""
import json
import falcon

class UploadCsvJsonResource(object):
  """For uploading and saving csv files as json for later analysis"""
  def on_post(self, req, resp):
    """Handles json file uploads"""
    resp.content_type = 'application/json'
    resp.status = falcon.HTTP_200
    uploadedJson = json.load(req.bounded_stream)['json']
    print(uploadedJson.keys())
    filename = uploadedJson['meta']['filename']
    with open('uploads/' + filename + '.json', 'w') as outfile:
      json.dump(uploadedJson, outfile)
    resp.body = json.dumps({'hello': 'world'})
