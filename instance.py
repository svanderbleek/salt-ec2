from boto import ec2
import time
from control import while_not_try
from region import region, ami

ec2 = ec2.connect_to_region(region())

aws_image = ami()
size = 't1.micro'

def start_instance(name, data):
  print('reserving instance for %s' % name)
  print(data)
  reserve_instance = lambda: ec2.run_instances(aws_image, key_name='sandy', user_data=data, instance_type=size, instance_profile_name=name)
  reservation = while_not_try(reserve_instance)
  instance = reservation.instances[0]
  print(instance)
  return instance

def wait_instance(queue):
  print('waiting for message from %s' % queue.name)
  get_message = lambda: queue.get_messages(wait_time_seconds=10)[0]
  while_not_try(get_message)

def stop_instance(instance):
  print('stopping instance for %s' % instance.id)
  instance.stop()
  status = instance.update()
  while status != 'stopped':
    print(status)
    status = instance.update()
    time.sleep(1)
