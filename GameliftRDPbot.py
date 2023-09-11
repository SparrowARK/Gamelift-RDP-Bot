import subprocess
import json

def remove_quotes(text):
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text

# Prompt the user for fleet ID and IP
fleet_id = input("Enter fleet ID: ")
my_ip = input("Enter your public IP: ")

# Execute command to describe instances
describe_instances_cmd = f"aws gamelift describe-instances --fleet-id {fleet_id}"
instances_output = subprocess.check_output(describe_instances_cmd, shell=True).decode()

# Extract instance ID from the output
instance_id = ""
for line in instances_output.splitlines():
    if "InstanceId" in line:
        instance_id = line.split(":")[1].strip()
        break

# Remove double quotes and any extra comma from the instance ID
instance_id = remove_quotes(instance_id).rstrip(',')

# Execute command to get instance access
get_instance_access_cmd = f"aws gamelift get-instance-access --fleet-id {fleet_id} --instance-id {instance_id}"
access_output = subprocess.check_output(get_instance_access_cmd, shell=True).decode()

# Parse the command output as JSON
parsed_data = json.loads(access_output)

# Extract the required information
username = parsed_data["InstanceAccess"]["Credentials"]["UserName"]
secret = parsed_data["InstanceAccess"]["Credentials"]["Secret"]
ip_address = parsed_data["InstanceAccess"]["IpAddress"]

# Check if the inbound rule already exists
check_rule_cmd = f"aws gamelift describe-fleet-port-settings --fleet-id {fleet_id}"
check_rule_output = subprocess.check_output(check_rule_cmd, shell=True).decode()
parsed_rules = json.loads(check_rule_output)["InboundPermissions"]

existing_rule = next((rule for rule in parsed_rules if rule["FromPort"] == 3389 and rule["ToPort"] == 3389 and rule["IpRange"] == f"{my_ip}/32" and rule["Protocol"] == "TCP"), None)

if existing_rule is not None:
    print("The inbound rule already exists.")
else:
    # Execute command to update fleet port settings
    update_port_settings_cmd = f"aws gamelift update-fleet-port-settings --fleet-id {fleet_id} --inbound-permission-authorizations FromPort=3389,ToPort=3389,IpRange={my_ip}/32,Protocol=TCP"
    subprocess.run(update_port_settings_cmd, shell=True)
    print("The inbound rule has been added.")

# Output the previous IP address, username, and password
print("Username:", username)
print("Secret:", secret)
print("IP Address:", ip_address)

input("\nPress Enter to exit...")