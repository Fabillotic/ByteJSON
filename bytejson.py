import json

class ClassFile:
    def __init__(self):
        pass

    @staticmethod
    def serialize(d):
        r = {}
        magic = d[:4]
        d = d[4:]
        
        minor = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        major = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["version"] = {"major": major, "minor": minor}
        r["pool"] = ConstPool.serialize(d)
        return r

    @staticmethod
    def deserialize(d):
        r = b""
        r += bytes.fromhex("CAFEBABE")
        
        r += d["version"]["minor"].to_bytes(2, "big")
        r += d["version"]["major"].to_bytes(2, "big")
        
        r += ConstPool.deserialize(d["pool"])
        return r

class ConstPool:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d):
        r = []
        
        l = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        i = 1
        while i < (l - 1):
            t = int.from_bytes(d[0], "big")
            d = d[1:]

            if t == 01: #UTF8
                l = int.from_bytes(d[:2], "big")
                d = d[2:]
                s = d[l:]
                d = d[:l]
                r.append({"type": "utf8", "data": s})
            elif t == 03: #Integer
                i = int.from_bytes(d[:4], "big")
                d = d[4:]
                r.append({"type": "int", "data": i})
            elif t == 04: #Float
            elif t == 05: #Long
            elif t == 06: #Double
        return r
    
    @staticmethod
    def deserialize(d):
        r = b""
        return r

class Field:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d):
        pass
    
    @staticmethod
    def deserialize(d):
        pass

class Method:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d):
        pass
    
    @staticmethod
    def deserialize(d):
        pass

class Attribute:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d):
        pass
    
    @staticmethod
    def deserialize(d):
        pass

if __name__ == "__main__":
    f = open("Main.class", "rb")
    d = f.read()
    print(d.hex())
    f.close()
    j = ClassFile.serialize(d)
    print(json.dumps(j))
    dn = ClassFile.deserialize(j)
    print(dn.hex())
