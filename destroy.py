import sys
import boto

timestamp = sys.argv[1]
master = 'salt-master-%s' % timestamp
minion = 'salt-minion-%s' % timestamp

autoscale = boto.connect_autoscale()
ec2 = boto.connect_ec2()

autoscale.delete_auto_scaling_group(master, force_delete=True)
autoscale.delete_auto_scaling_group(minion, force_delete=True)
autoscale.delete_launch_configuration(master)
autoscale.delete_launch_configuration(minion)

print('deleting security groups')
deleted = False
while not deleted:
  print('.')
  try:
    ec2.delete_security_group(master)
    ec2.delete_security_group(minion)
    deleted = True
  except:
    pass
