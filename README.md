# ByteJSON
Serialize Java class files to JSON

## Usage
```python3
from bytejson import ClassFile

jdata = ClassFile.serialize(data) #Turn the class data to json.
ndata = ClassFile.deserialize(jdata) #Turn the json data back to the class data.

#Both data and ndata should not differ as jdata wasn't altered.
assert data == ndata
```
