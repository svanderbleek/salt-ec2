import boto
import base64
from string import Template
import time
import sys

timestamp = int(time.time())
name = 'salt-image-%d' % timestamp
print(name)

sqs = boto.connect_sqs()
queue = sqs.create_queue('boto-ec2-queue')

aws_image = 'ami-fb8e9292'
size = 't1.micro'

mapping = {'queue_url': queue.url}
template = open('image_user_data.template').read()
template = Template(template)
data = template.substitute(mapping)
data = base64.b64encode(data)

iam = boto.connect_iam()
policy = open('image_policy.json').read()
iam.create_instance_profile(name)
iam.create_role(name)
iam.put_role_policy(name, name, policy)
iam.add_role_to_instance_profile(name, name)

ec2 = boto.connect_ec2()
reservation = None
print('reserving instance')
while not reservation:
  print('.')
  try:
    reservation = ec2.run_instances(aws_image, user_data=data, instance_type=size, instance_profile_name=name)
  except:
    pass
  time.sleep(1)
instance = reservation.instances[0]
print(instance)

message = None
print('waiting for signal')
while not message:
  print('.')
  try:
    message = sqs.receive_message(queue, wait_time_seconds=5)[0]
    sqs.delete_message(queue, message)
  except:
    pass
print(message)

print('stopping instance')
instance.stop()
status = ''
while status != 'stopped':
  status = instance.update()
  print(status)
  time.sleep(1)
salt_image = instance.create_image(name)
print(salt_image)

instance.terminate()
iam.delete_role_policy(name, name)
iam.remove_role_from_instance_profile(name, name)
iam.delete_role(name)
iam.delete_instance_profile(name)
