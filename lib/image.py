import time
from boto import sqs
from multiprocessing import Pool
from identity import identify
from data import user_data
from access import create_policy, delete_policy
from instance import start_instance, wait_instance, stop_instance
from region import region

sqs = sqs.connect_to_region(region())

def build_image(image_type):
  name, data, queue = setup(image_type)
  instance = start_instance(name, data)
  wait_instance(queue)
  stop_instance(instance)
  salt_image = instance.create_image(name)
  print(salt_image)
  cleanup(name, instance, queue)

def setup(image_type):
  name = 'salt-%s' % image_type
  name = identify(name)
  print(name)
  create_policy(name, 'image_policy.json')
  queue = sqs.create_queue(name)
  mapping = {'region': region(), 'queue_url': queue.url, 'image_type': image_type}
  data = user_data('image_data', mapping)
  return name, data, queue

def cleanup(name, instance, queue):
  instance.terminate()
  delete_policy(name)
  queue.delete()

def build_images_async():
  pool = Pool()
  master = pool.apply_async(build_image, ['master'])
  minion = pool.apply_async(build_image, ['minion'])
  pool.close()
  pool.join()
  master.get()
  minion.get()

build_images_async()
