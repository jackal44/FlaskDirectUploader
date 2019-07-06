

from flask import Flask, render_template, request, redirect, url_for, flash
import os, json, boto3, botocore
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

app = Flask(__name__)


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
  string=str(path)
  try:
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
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    ExpiresIn = 3600,
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port = port)
