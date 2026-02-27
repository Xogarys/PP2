import json

# Read and parse the JSON file
with open('sample-data.json', 'r') as file:
    data = json.load(file)   # Load the entire JSON file into a Python dictionary

# Print the table header with formatted columns
print("Interface Status")
print("=" * 50)

# Each column is left-aligned with a fixed width for a clean table look
print(f"{'DN':<50} {'Description':<20} {'Speed':<10} {'MTU':<10}")
print(f"{'-'*50} {'-'*20} {'-'*10} {'-'*10}")  # Separator line under the header

# Loop through each interface and print its details
for item in data['imdata']:
    attributes = item['l1PhysIf']['attributes']  # Navigate to the attributes of each interface

    dn    = attributes['dn']                                        # Distinguished Name — unique path of the interface
    descr = attributes['descr'] if attributes['descr'] else ""      # Use empty string if description is missing
    speed = attributes['speed']                                     # Interface speed (e.g. 1G, 10G)
    mtu   = attributes['mtu']                                       # Maximum Transmission Unit size

    # Print each interface as a formatted row aligned with the header columns
    print(f"{dn:<50} {descr:<20} {speed:<10} {mtu:<10}")
