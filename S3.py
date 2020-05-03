import boto3

s3 = boto3.client('s3')

#s3.create_bucket(Bucket='findtroll-metadata' , CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-2'})

filename = 'champion.csv'
bucket_name = 'findtroll-metadata'
s3.upload_file(filename,bucket_name,filename)

filename = 'item.csv'
bucket_name = 'findtroll-metadata'
s3.upload_file(filename,bucket_name,filename)

filename = 'spell.csv'
bucket_name = 'findtroll-metadata'
s3.upload_file(filename,bucket_name,filename)

