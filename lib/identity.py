import time

def make_timestamp():
  return int(time.time())

default = make_timestamp()

def identify(name, identifier=''):
  identifier = str(identifier) or default
  return name + '-%d' % identifier
