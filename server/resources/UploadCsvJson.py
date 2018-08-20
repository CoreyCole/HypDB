"""Upload Csv Json"""
import json
import falcon
import csv

class UploadCsvJsonResource(object):
  """For uploading and saving csv files as json for later analysis"""
  def on_post(self, req, resp):
    """Handles json file uploads"""
    resp.content_type = 'application/json'
    resp.status = falcon.HTTP_200
    uploadedJson = json.load(req.bounded_stream)['json']
    meta = uploadedJson['meta']
    filename = uploadedJson['meta']['filename']
    with open('uploads/' + filename + '.json', 'w') as outfile:
        json.dump(meta, outfile)
    with open('./tmp/' + filename, 'w') as g:
        fieldnames = meta['fields']
        writer = csv.DictWriter(g, fieldnames=fieldnames)
        writer.writeheader()
        for line in uploadedJson['data']:
            if len(line) == len(fieldnames):
                writer.writerow(line)
    resp.body = json.dumps({'message': 'success'})
