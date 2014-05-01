import sys
from boto import ec2

try:
  aws_region = sys.argv[1]
except IndexError:
  aws_region = 'us-east-1'

region_image_map = {
  'us-east-1': 'ami-fb8e9292',
  'us-west-1': 'ami-7aba833f'
}

def region():
  return aws_region

def ami():
  return region_image_map[aws_region]
