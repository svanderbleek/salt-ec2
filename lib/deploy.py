import sys
import time
import boto
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from data import user_data, env
from identity import identify
from region import region
from access import create_policy
from control import while_not_try

autoscale = boto.ec2.autoscale.connect_to_region(region())
ec2 = boto.ec2.connect_to_region(region())
route53 = boto.connect_route53()

ami_timestamp = sys.argv[2]
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

zone = route53.get_zones()[0]
mapping = {'zone_id': zone.id, 'dns': env('salt_master_dns')}
master_data = user_data('master_data', mapping)
create_policy(master, 'master_policy.json')
master_config = LaunchConfiguration(
  name=master,
  image_id=master_ami,
  security_groups=[master_security.name],
  user_data=master_data,
  key_name='sandy',
  instance_profile_name=master
)
while_not_try(lambda: autoscale.create_launch_configuration(master_config))
master_group = AutoScalingGroup(
  group_name=master,
  launch_config=master_config,
  availability_zones=[region() + 'a'],
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
  availability_zones=[region() + 'a'],
  min_size=10,
  max_size=10
)
autoscale.create_auto_scaling_group(minion_group)
