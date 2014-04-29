import os
import time
import boto
from string import Template
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup

timestamp = int(time.time())
master = 'salt-master-%d' % timestamp
minion = 'salt-minion-%d' % timestamp
image = os.environ['SALT_AMI']

autoscale = boto.connect_autoscale()
ec2 = boto.connect_ec2()

master_security = ec2.create_security_group(master, master)
minion_security = ec2.create_security_group(minion, minion)
master_security.authorize(src_group=minion_security)

master_data = open('master_user_data').read()
master_config = LaunchConfiguration(
  name=master,
  image_id=image,
  security_groups=[master_security.name],
  user_data=master_data,
  key_name='sandy'
)
autoscale.create_launch_configuration(master_config)
master_group = AutoScalingGroup(
  group_name=master,
  launch_config=master_config,
  availability_zones=['us-east-1a'],
  min_size=1,
  max_size=1
)
autoscale.create_auto_scaling_group(master_group)

mapping = {'master': os.environ['SALT_MASTER_DNS']}
template = open('minion_user_data.template').read()
template = Template(template)
data = template.substitute(mapping)
minion_data = base64.b64encode(data)
minion_config = LaunchConfiguration(
  name=minion,
  image_id=image,
  security_groups=[minion_security.name],
  user_data=minion_data,
  key_name='sandy'
)
autoscale.create_launch_configuration(minion_config)
minion_group = AutoScalingGroup(
  group_name=minion,
  launch_config=minion_config,
  availability_zones=['us-east-1a', 'us-east-1b'],
  min_size=2,
  max_size=2
)
autoscale.create_auto_scaling_group(minion_group)
