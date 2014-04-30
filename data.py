import os
from string import Template
from base64 import b64encode

def user_data(data, mapping=None, encode=False):
  content = open(data).read()
  if mapping:
    template = Template(content)
    content = template.substitute(mapping)
  if encode:
    content = b64encode(content)
  return content

def env(key):
  key = key.upper()
  return os.environ(key)
