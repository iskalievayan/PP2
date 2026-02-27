import json

#eg1
python_dict = {
    "name": "Alice",
    "age": 25,
    "city": "London"
}

json_string = json.dumps(python_dict)
print(json_string)
print("Type:", type(json_string))

#eg2
python_data = {
    "name": "Bob",
    "age": 30,
    "hobbies": ["reading", "gaming", "coding"],
    "address": {
        "street": "123 Main St",
        "city": "New York"
    }
}

json_formatted = json.dumps(python_data, indent=4)
print(json_formatted)

#eg3
python_types = {
    "string": "hello",
    "number": 42,
    "float": 3.14,
    "boolean": True,
    "null": None,
    "list": [1, 2, 3],
    "dict": {"key": "value"}
}

json_output = json.dumps(python_types, indent=2)
print(json_output)