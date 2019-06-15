####
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


from flask import Flask, render_template, request, redirect, url_for
import os, json, boto3, botocore
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError
from flask_util_js import FlaskUtilJs
import threading, sys
from boto3.s3.transfer import TransferConfig

app = Flask(__name__)
fujs=FlaskUtilJs(app)

@app.context_processor
def inject_fujs():
  return dict(fujs=fujs)

client=boto3.client('s3','ap-southeast-1')
transfer =S3Transfer(client)
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
s3 = boto3.client(
  's3',
  aws_access_key_id=S3_ACCESS_KEY_ID,
  aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


@app.route("/account/")
def account():
  # receive file, then pass it on
  return render_template('account.html')

@app.route("/submit-form/", methods = ["POST"])
def submit_form():
  return render_template('profile.html')

@app.route('/new/')
def show():
  keys=[]
  resp=s3.list_objects_v2(Bucket=S3_BUCKET)
  for obj in resp['Contents']:
    keys.append(obj['Key'])
  return render_template('new.html',keys=keys)

@app.route('/download/')
def download():
  object=request.args.get('object')
  service=boto3.resource('s3')
  path=os.getcwd()+"\\"+object
  try:
    # progress=ProgressPercentage(transfer._manager._client, S3_BUCKET, path, data=object)
    transfer.download_file(S3_BUCKET, object, path)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      alert("The object does not exist.")
    else:
      raise
  return json.dumps({
    'data': 'successfully downloaded files!'
  })



@app.route('/sign-s3/')
def sign_s3():
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')

  GB=1024**3
  # config=TransferConfig(multipart_threshold=5*GB)
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    ExpiresIn = 3600,
    # Config=config
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

# WIP - download progress bar
# class ProgressPercentage(object):
#   def __init__(self, client, bucket, filename, data):
#     self._filename=filename
#     self._size=float(os.path.getsize(filename))
#     self._seen_so_far =0
#     self._lock = threading.Lock()
#     self._size=client.head_object(Bucket=S3_BUCKET, Key=data)['ContentLength']

#   def __call__(self, bytes_amount):
#     with self._lock:
#       self._seen_so_far+=bytes_amount
#       percentage=(self._seen_so_far/self._size)*100
#       # LoggingFile('{} is the filename, {} out of {} done. The percentage completed is {} %'.format(str(self._filename), str(self._seen_so_far), str(self._size), str(percentage)))
#       sys.stdout.flush()

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port = port)
