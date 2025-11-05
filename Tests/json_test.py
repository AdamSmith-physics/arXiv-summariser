import json

def load_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Example usage
json_data = load_json_file('test_json_file.json')
print(json_data)

print(f"Categories: ", json_data['Categories'])

print(f"Categories[0]: ", json_data['Categories'][0])