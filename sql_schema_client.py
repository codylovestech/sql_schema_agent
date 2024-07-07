import os

# remove the "result.sql" file
#if os.path.exists("result.sql"):
#    os.remove("result.sql")

# call POST to localhost:5000/create with the data from the "sample.json" file
import requests
import json

with open("sample.json", "r") as f:
    data = json.load(f)

remove_nodes = []
# remove all nodes when name is already in result.sql
for node in data["nodes"]:
    if os.path.exists("result.sql"):
        with open("result.sql", "r") as f:
            if "-- " + node["id"] + "\n" in f.read():
                remove_nodes.append(node)
            if "-- "+node["data"]["name"]+"\n" in f.read():
                remove_nodes.append(node)

for node in remove_nodes:
    data["nodes"].remove(node)


response = requests.post("http://127.0.0.1:5000/create", json={
    "data": data,
    "technology": "PostgreSQL"
}, stream=True, headers={
    "Content-Type": "application/json"
})
# read each line because the response is a stream
for line in response.iter_lines():
    # append the line to the "result.sql" file
    with open("result.sql", "a") as f:
        try:
            j = json.loads(line.decode("utf-8"))
            if j.get("result"):
                f.write("-- " + j["table"] + "\n")
                print(j["result"])
                f.write(j["result"] + "\n")
                # flus
                f.flush()
            if j.get("progress"):
                print(j["progress"])
        except Exception as e:
            print(line)
            print(e)





