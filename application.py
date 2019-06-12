####
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


from flask import Flask, render_template, request, redirect, url_for
import os, json, boto3, botocore


app = Flask(__name__)


# Load necessary information into the application
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
s3 = boto3.client(
  's3',
  aws_access_key_id=S3_ACCESS_KEY_ID,
  aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

relative_path='./images'
abs_path=os.path.abspath(relative_path)

# Listen for GET requests to yourdomain.com/account/
@app.route("/account/")
def account():
  # receive file, then pass it on
  return render_template('account.html')


# Listen for POST requests to yourdomain.com/submit_form/
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

@app.route('/download/<object>')
def download(object):
  file=os.getcwd()+"\\"+object
  service=boto3.resource('s3')
  try:
    r=service.Bucket(S3_BUCKET).download_file(object, file)
  except botocore.exceptions.Client as e:
    if e.response['Error']['Code'] == "404":
      alert("The object does not exist.")
    else:
      raise
  return redirect(url_for('account'))



@app.route('/sign-s3/')
def sign_s3():
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    ExpiresIn = 3600
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port = port)
