import boto

iam = boto.connect_iam()

def create_policy(name, json):
  policy = open(json).read()
  iam.create_instance_profile(name)
  iam.create_role(name)
  iam.put_role_policy(name, name, policy)
  iam.add_role_to_instance_profile(name, name)

def delete_policy(name):
  iam.delete_role_policy(name, name)
  iam.remove_role_from_instance_profile(name, name)
  iam.delete_role(name)
  iam.delete_instance_profile(name)
