import time
from boto.exception import BotoServerError, BotoClientError

def while_not_try(fetch, sleep=1):
  concern = None
  while not concern:
    print('.')
    try:
      concern = fetch()
      print(concern)
    except (BotoServerError, BotoClientError, IndexError):
      pass
    time.sleep(sleep)
  return concern
