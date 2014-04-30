import sys
import time
import boto
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from data import user_data, env
from identity import identify

autoscale = boto.connect_autoscale()
ec2 = boto.connect_ec2()
route53 = boto.connect_route53()

ami_timestamp = sys.argv[1]
master_ami = 'salt-master-%s' % ami_timestamp
minion_ami = 'salt-minion-%s' % ami_timestamp
images = ec2.get_all_images(owners=['self'])
master_ami = [image.id for image in images if image.name == master_ami][0]
minion_ami = [image.id for image in images if image.name == minion_ami][0]

master = identify('salt-master')
minion = identify('salt-minion')

master_security = ec2.create_security_group(master, master)
minion_security = ec2.create_security_group(minion, minion)
master_security.authorize(src_group=minion_security)

master_data = user_data('master_data')
master_config = LaunchConfiguration(
  name=master,
  image_id=master_ami,
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

mapping = {'master': env('salt_master_dns')}
minion_data = user_data('minion_data', mapping)
minion_config = LaunchConfiguration(
  name=minion,
  image_id=minion_ami,
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
