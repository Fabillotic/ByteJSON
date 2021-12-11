import json
import struct

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
        r["pool"], d = ConstPool.serialize(d)
        
        r["access_flags"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["this_class"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["super_class"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["interfaces"] = []
        
        ic = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        for i in range(ic):
            r["interfaces"].append(int.from_bytes(d[:2], "big"))
            d = d[2:]
        
        r["fields"] = []
        
        fc = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        for i in range(fc):
            f, d = Field.serialize(d, r["pool"])
            r["fields"].append(f)
        
        r["methods"] = []
        
        mc = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        for i in range(mc):
            m, d = Method.serialize(d, r["pool"])
            r["methods"].append(m)
        
        r["attributes"] = []
        
        ac = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        for i in range(ac):
            a, d = Attribute.serialize(d, r["pool"])
            r["attributes"].append(a)

        
        return r

    @staticmethod
    def deserialize(d):
        r = b""
        r += bytes.fromhex("CAFEBABE")
        
        r += d["version"]["minor"].to_bytes(2, "big")
        r += d["version"]["major"].to_bytes(2, "big")
        
        r += ConstPool.deserialize(d["pool"])

        r += d["access_flags"].to_bytes(2, "big")
        r += d["this_class"].to_bytes(2, "big")
        r += d["super_class"].to_bytes(2, "big")
        
        r += len(d["interfaces"]).to_bytes(2, "big")
        for i in d["interfaces"]:
            r += i.to_bytes(2, "big")

        r += len(d["fields"]).to_bytes(2, "big")
        for f in d["fields"]:
            r += Field.deserialize(f)
        
        r += len(d["methods"]).to_bytes(2, "big")
        for m in d["methods"]:
            r += Method.deserialize(m)
        
        r += len(d["attributes"]).to_bytes(2, "big")
        for a in d["attributes"]:
            r += Attribute.deserialize(a)
        
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
        while i < l:
            t = int.from_bytes(d[:1], "big")
            d = d[1:]

            if t ==   1: #UTF8
                sl = int.from_bytes(d[:2], "big")
                d = d[2:]
                s = d[:sl].decode("utf8")
                d = d[sl:]
                r.append({"index": i, "type": "utf8", "data": s})
            elif t ==  3: #Integer
                n = struct.unpack(">i", d[:4])[0]
                d = d[4:]
                r.append({"index": i, "type": "int", "data": n})
            elif t ==  4: #Float
                f = struct.unpack(">f", d[:4])[0]
                d = d[4:]
                r.append({"index": i, "type": "float", "data": f})
            elif t ==  5: #Long
                n = struct.unpack(">q", d[:8])[0]
                d = d[8:]
                r.append({"index": i, "type": "long", "data": n})
                i += 1
            elif t ==  6: #Double
                n = struct.unpack(">d", d[:8])[0]
                d = d[8:]
                r.append({"index": i, "type": "double", "data": n})
                i += 1
            elif t ==  7: #Class
                n = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "class", "data": n})
            elif t ==  8: #String
                n = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "string", "data": n})
            elif t ==  9: #Field
                c = int.from_bytes(d[:2], "big")
                d = d[2:]
                nt = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "field", "data": {"class": c, "name_type": nt}})
            elif t == 10: #Method
                c = int.from_bytes(d[:2], "big")
                d = d[2:]
                nt = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "method", "data": {"class": c, "name_type": nt}})
            elif t == 11: #Interface method
                c = int.from_bytes(d[:2], "big")
                d = d[2:]
                nt = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "interface_method", "data": {"class": c, "name_type": nt}})
            elif t == 12: #Name and type
                n = int.from_bytes(d[:2], "big")
                d = d[2:]
                nt = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "name_type", "data": {"name": n, "type": nt}})
            elif t == 15: #Method handle
                rk = int.from_bytes(d[:1], "big")
                d = d[1:]
                ri = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "method_handle", "data": {"reference_kind": rk, "reference_index": ri}})
            elif t == 16: #Method type
                di = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "method_type", "data": di})
            elif t == 18: #Invoke dynamic
                bi = int.from_bytes(d[:2], "big")
                d = d[2:]
                nt = int.from_bytes(d[:2], "big")
                d = d[2:]
                r.append({"index": i, "type": "invoke_dynamic", "data": {"bootstrap_method_attr_index": bi, "name_type": nt}})
            
            i += 1
        
        return r, d
    
    @staticmethod
    def deserialize(d):
        r = b""
        
        r += (d[-1]["index"] + 1).to_bytes(2, "big")
        m = 0
        
        for e in d:
            if e["index"] > m:
                m = e["index"]

        for i in range(1, m + 1):
            for e in d:
                if e["index"] == i:
                    t = e["type"]
                    if t == "utf8":
                        s = e["data"].encode("utf8")
                        r += b"\x01" + len(s).to_bytes(2, "big") + s
                    elif t == "int":
                        r += b"\x03" + struct.pack(">i", e["data"])
                    elif t == "float":
                        r += b"\x04" + struct.pack(">f", e["data"])
                    elif t == "long":
                        r += b"\x05" + struct.pack(">q", e["data"])
                    elif t == "double":
                        r += b"\x06" + struct.pack(">d", e["data"])
                    elif t == "class":
                        r += b"\x07" + e["data"].to_bytes(2, "big")
                    elif t == "string":
                        r += b"\x08" + e["data"].to_bytes(2, "big")
                    elif t == "field":
                        r += b"\x09" + e["data"]["class"].to_bytes(2, "big") + e["data"]["name_type"].to_bytes(2, "big")
                    elif t == "method":
                        r += b"\x0A" + e["data"]["class"].to_bytes(2, "big") + e["data"]["name_type"].to_bytes(2, "big")
                    elif t == "interface_method":
                        r += b"\x0B" + e["data"]["class"].to_bytes(2, "big") + e["data"]["name_type"].to_bytes(2, "big")
                    elif t == "name_type":
                        r += b"\x0C" + e["data"]["name"].to_bytes(2, "big") + e["data"]["type"].to_bytes(2, "big")
                    elif t == "method_handle":
                        r += b"\x0F" + e["data"]["reference_kind"].to_bytes(1, "big") + e["data"]["reference_index"].to_bytes(2, "big")
                    elif t == "method_type":
                        r += b"\x10" + e["data"].to_bytes(2, "big")
                    elif t == "invoke_dynamic":
                        r += b"\x12" + e["data"]["bootstrap_method_attr_index"].to_bytes(2, "big") + e["data"]["name_type"].to_bytes(2, "big")
                    break
        
        return r

class Field:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d, cpool):
        r = {}
        
        r["access_flags"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["name"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["type"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        ac = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["attributes"] = []
        
        for i in range(ac):
            a, d = Attribute.serialize(d, cpool)
            r["attributes"].append(a)
        
        return r, d
    
    @staticmethod
    def deserialize(d):
        r = b""
        
        r += d["access_flags"].to_bytes(2, "big")
        r += d["name"].to_bytes(2, "big")
        r += d["type"].to_bytes(2, "big")
        
        r += len(d["attributes"]).to_bytes(2, "big")
        for a in d["attributes"]:
            r += Attribute.deserialize(a)
        
        return r

class Method:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d, cpool):
        r = {}
        
        r["access_flags"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["name"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["type"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        ac = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        r["attributes"] = []
        
        for i in range(ac):
            a, d = Attribute.serialize(d, cpool)
            r["attributes"].append(a)
        
        return r, d
    
    @staticmethod
    def deserialize(d):
        r = b""
        
        r += d["access_flags"].to_bytes(2, "big")
        r += d["name"].to_bytes(2, "big")
        r += d["type"].to_bytes(2, "big")
        
        r += len(d["attributes"]).to_bytes(2, "big")
        for a in d["attributes"]:
            r += Attribute.deserialize(a)
        
        return r

class Attribute:
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(d, cpool):
        r = {"type": None}
        
        r["name_index"] = int.from_bytes(d[:2], "big")
        d = d[2:]
        
        t = None
        for x in cpool:
            if x["index"] == r["name_index"]:
                t = x["data"]
        
        l = int.from_bytes(d[:4], "big")
        d = d[4:]
        
        c = False
        if t:
            c = True
            if t.lower() == "constantvalue":
                r["data"] = int.from_bytes(d[:2], "big")
                d = d[2:]
            elif t.lower() == "code":
                r["data"] = {}
                r["data"]["max_stack"] = int.from_bytes(d[:2], "big")
                d = d[2:]
                r["data"]["max_locals"] = int.from_bytes(d[:2], "big")
                d = d[2:]
                
                codelen = int.from_bytes(d[:4], "big")
                d = d[4:]
                
                code = d[:codelen]
                d = d[codelen:]
                
                r["data"]["code"] = code.hex()
                
                elen = int.from_bytes(d[:2], "big")
                d = d[2:]
                
                r["data"]["exceptions"] = []
                
                for i in range(elen):
                    e = {}
                    e["start_pc"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    e["end_pc"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    e["handler_pc"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    e["catch_type"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    r["data"]["exceptions"].append(e)

                ac = int.from_bytes(d[:2], "big")
                d = d[2:]
                
                r["data"]["attributes"] = []
                
                for i in range(ac):
                    a, d = Attribute.serialize(d, cpool)
                    r["data"]["attributes"].append(a)
            elif t.lower() == "exceptions":
                r["data"] = []

                elen = int.from_bytes(d[:2], "big")
                d = d[2:]
                
                for i in range(elen):
                    r["data"].append(int.from_bytes(d[:2], "big"))
                    d = d[2:]
            elif t.lower() == "innerclasses":
                r["data"] = []
                
                ilen = int.from_bytes(d[:2], "big")
                d = d[2:]
                
                for i in range(ilen):
                    cl = {}
                    cl["inner_class_info_index"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    cl["outer_class_info_index"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    cl["inner_name_index"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    cl["inner_class_access_flags"] = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    r["data"].append(cl)
            elif t.lower() == "sourcefile":
                r["data"] = int.from_bytes(d[:2], "big")
                d = d[2:]
            elif t.lower() == "synthetic":
                r["data"] = None
            elif t.lower() == "deprecated":
                r["data"] = None
            elif t.lower() == "enclosingmethod":
                r["data"] = {}
                r["data"]["class_index"] = int.from_bytes(d[:2], "big")
                d = d[2:]
                r["data"]["method_index"] = int.from_bytes(d[:2], "big")
                d = d[2:]
            elif t.lower() == "stackmaptable":
                #sd = d[:l]
                smt = d[:l]
                #print("StackMapTable:", sd.hex())
                
                es = int.from_bytes(smt[:2], "big")
                smt = smt[2:]

                def verification_type_info(smt, n): #Read n verification_type_info structures
                    vtypes = []
                    for i in range(n):
                        vtag = int.from_bytes(smt[:1], "big")
                        smt = smt[1:]

                        if vtag == 0: #top
                            vtypes.append({"type": "top"})
                        elif vtag == 1: #int
                            vtypes.append({"type": "int"})
                        elif vtag == 2: #float
                            vtypes.append({"type": "float"})
                        elif vtag == 3: #double
                            vtypes.append({"type": "double"})
                        elif vtag == 4: #long
                            vtypes.append({"type": "long"})
                        elif vtag == 5: #null
                            vtypes.append({"type": "null"})
                        elif vtag == 6: #uninitializedThis
                            vtypes.append({"type": "uninitializedThis"})
                        elif vtag == 7: #object
                            vtypes.append({"type": "object", "index": int.from_bytes(smt[:2], "big")})
                            smt = smt[2:]
                        elif vtag == 8: #uninitialized
                            vtypes.append({"type": "uninitialized", "offset": int.from_bytes(smt[:2], "big")})
                            smt = smt[2:]
                    return smt, vtypes

                r["data"] = []
                
                while len(smt) > 0:
                    tag = int.from_bytes(smt[:1], "big")
                    smt = smt[1:]
                    
                    frame = None
                    if tag >= 0 and tag <= 63: #same_frame
                        frame = {"tag": tag, "frame": "same_frame", "offset_delta": tag}
                    elif tag >= 64 and tag <= 127: #same_locals_1_stack_item_frame
                        smt, vti = verification_type_info(smt, 1)
                        frame = {"tag": tag, "frame": "same_locals_1_stack_item_frame", "offset_delta": tag - 64, "stack": vti}
                    elif tag == 247: #same_locals_1_stack_item_frame_extended
                        offset_delta = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        smt, vti = verification_type_info(smt, 1)
                        frame = {"tag": tag, "frame": "same_locals_1_stack_item_frame_extended", "offset_delta": offset_delta, "stack": vti}
                    elif tag >= 248 and tag <= 250: #chop_frame
                        offset_delta = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        frame = {"tag": tag, "frame": "chop_frame", "offset_delta": offset_delta, "locals_absent": 251 - tag}
                    elif tag == 251: #same_frame_extended
                        offset_delta = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        frame = {"tag": tag, "frame": "same_frame_extended", "offset_delta": offset_delta}
                    elif tag >= 252 and tag <= 254: #append_frame
                        offset_delta = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        locals_plus = tag - 251
                        smt, vti = verification_type_info(smt, locals_plus)
                        frame = {"tag": tag, "frame": "append_frame", "offset_delta": offset_delta, "locals": vti}
                    elif tag == 255:
                        offset_delta = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        number_of_locals = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        smt, all_locals = verification_type_info(smt, number_of_locals)
                        number_of_stack_items = int.from_bytes(smt[:2], "big")
                        smt = smt[2:]
                        smt, stack = verification_type_info(smt, number_of_stack_items)
                        frame = {"tag": tag, "frame": "full_frame", "offset_delta": offset_delta, "locals": all_locals, "stack": stack}

                    r["data"].append(frame)
                
                #r["data"] = sd.hex()
                d = d[l:]
            elif t.lower() == "signature":
                r["data"] = int.from_bytes(d[:2], "big")
                d = d[2:]
            elif t.lower() == "linenumbertable":
                tl = int.from_bytes(d[:2], "big")
                d = d[2:]

                r["data"] = []

                for i in range(tl):
                    r["data"].append({"start_pc": int.from_bytes(d[:2], "big"), "line_number": int.from_bytes(d[2:4], "big")})
                    d = d[4:]
            elif t.lower() == "localvariabletable":
                tl = int.from_bytes(d[:2], "big")
                d = d[2:]

                r["data"] = []

                for i in range(tl):
                    start_pc = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    length = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    name_index = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    descriptor_index = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    index = int.from_bytes(d[:2], "big")
                    d = d[2:]
                    r["data"].append({"start_pc": start_pc, "length": length, "name_index": name_index, "descriptor_index": descriptor_index, "index": index})
            else:
                c = False
        
        if c:
            r["type"] = t
        else:
            r["data"] = d[:l].hex()
            d = d[l:]
        
        return r, d
    
    @staticmethod
    def deserialize(d):
        r = b""
        
        r += d["name_index"].to_bytes(2, "big")
        
        if d["type"] == None:
            ad = bytes.fromhex(d["data"])
            
            r += len(ad).to_bytes(4, "big")
            r += ad
        elif d["type"].lower() == "constantvalue":
            tmp = b""

            tmp += d["data"].to_bytes(2, "big")

            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "code":
            tmp = b""
            
            tmp += d["data"]["max_stack"].to_bytes(2, "big")
            tmp += d["data"]["max_locals"].to_bytes(2, "big")
            
            code = bytes.fromhex(d["data"]["code"])
            tmp += len(code).to_bytes(4, "big")
            tmp += code
            
            tmp += len(d["data"]["exceptions"]).to_bytes(2, "big")
            for e in d["data"]["exceptions"]:
                tmp += e["start_pc"].to_bytes(2, "big")
                tmp += e["end_pc"].to_bytes(2, "big")
                tmp += e["handler_pc"].to_bytes(2, "big")
                tmp += e["catch_type"].to_bytes(2, "big")

            tmp += len(d["data"]["attributes"]).to_bytes(2, "big")
            for a in d["data"]["attributes"]:
                tmp += Attribute.deserialize(a)
            
            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "exceptions":
            tmp = b""

            tmp += len(d["data"]).to_bytes(2, "big")
            for e in d["data"]:
                tmp += e.to_bytes(2, "big")
            
            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "innerclasses":
            tmp = b""
            
            tmp += len(d["data"]).to_bytes(2, "big")
            for i in d["data"]:
                tmp += i["inner_class_info_index"].to_bytes(2, "big")
                tmp += i["outer_class_info_index"].to_bytes(2, "big")
                tmp += i["inner_name_index"].to_bytes(2, "big")
                tmp += i["inner_class_access_flags"].to_bytes(2, "big")
            
            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "sourcefile":
            r += b"\x00\x00\x00\x02"
            r += d["data"].to_bytes(2, "big")
        elif d["type"].lower() == "synthetic":
            r += b"\x00\x00\x00\x00"
        elif d["type"].lower() == "deprecated":
            r += b"\x00\x00\x00\x00"
        elif d["type"].lower() == "enclosingmethod":
            tmp = b""
            tmp += d["data"]["class_index"].to_bytes(2, "big")
            tmp += d["data"]["method_index"].to_bytes(2, "big")

            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "stackmaptable":
            tmp = b""

            def verification_type_info(vti):
                vto = b""
                for i in vti:
                    if i["type"] == "top":
                        vto += b"\x00"
                    elif i["type"] == "int":
                        vto += b"\x01"
                    elif i["type"] == "float":
                        vto += b"\x02"
                    elif i["type"] == "double":
                        vto += b"\x03"
                    elif i["type"] == "long":
                        vto += b"\x04"
                    elif i["type"] == "null":
                        vto += b"\x05"
                    elif i["type"] == "uninitializedThis":
                        vto += b"\x06"
                    elif i["type"] == "object":
                        vto += b"\x07"
                        vto += i["index"].to_bytes(2, "big")
                    elif i["type"] == "uninitialized":
                        vto += b"\x08"
                        vto += i["offset"].to_bytes(2, "big")
                return vto
            
            tmp += len(d["data"]).to_bytes(2, "big")
            
            for frame in d["data"]:
                tmp += frame["tag"].to_bytes(1, "big")

                if frame["frame"] == "same_frame": #same_frame, add no more information
                    pass
                elif frame["frame"] == "same_locals_1_stack_item_frame":
                    tmp += verification_type_info(frame["stack"])
                elif frame["frame"] == "same_locals_1_stack_item_frame_extended":
                    tmp += frame["offset_delta"].to_bytes(2, "big")
                    tmp += verification_type_info(frame["stack"])
                elif frame["frame"] == "chop_frame":
                    tmp += frame["offset_delta"].to_bytes(2, "big")
                elif frame["frame"] == "same_frame_extended":
                    tmp += frame["offset_delta"].to_bytes(2, "big")
                elif frame["frame"] == "append_frame":
                    tmp += frame["offset_delta"].to_bytes(2, "big")
                    tmp += verification_type_info(frame["locals"])
                elif frame["frame"] == "full_frame":
                    tmp += frame["offset_delta"].to_bytes(2, "big")
                    tmp += len(frame["locals"]).to_bytes(2, "big")
                    tmp += verification_type_info(frame["locals"])
                    tmp += len(frame["stack"]).to_bytes(2, "big")
                    tmp += verification_type_info(frame["stack"])

            #print("StackMapTable:", tmp.hex())
            #ad = bytes.fromhex(d["data"])
            
            #r += len(ad).to_bytes(4, "big")
            #r += ad

            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "signature":
            r += b"\x00\x00\x00\x02"
            r += d["data"].to_bytes(2, "big")
        elif d["type"].lower() == "linenumbertable":
            tmp = b""
            tmp += len(d["data"]).to_bytes(2, "big")
            for x in d["data"]:
                tmp += x["start_pc"].to_bytes(2, "big")
                tmp += x["line_number"].to_bytes(2, "big")
            
            r += len(tmp).to_bytes(4, "big")
            r += tmp
        elif d["type"].lower() == "localvariabletable":
            tmp = b""
            tmp += len(d["data"]).to_bytes(2, "big")
            for x in d["data"]:
                tmp += x["start_pc"].to_bytes(2, "big")
                tmp += x["length"].to_bytes(2, "big")
                tmp += x["name_index"].to_bytes(2, "big")
                tmp += x["descriptor_index"].to_bytes(2, "big")
                tmp += x["index"].to_bytes(2, "big")
            
            r += len(tmp).to_bytes(4, "big")
            r += tmp
        return r

if __name__ == "__main__":
    f = open("Main.class", "rb")
    d = f.read()
    f.close()
    
    j = ClassFile.serialize(d)
    print(json.dumps(j, indent=4))
    
    dn = ClassFile.deserialize(j)

    f = open("Main_.class", "wb")
    f.write(dn)
    f.close()
    
    print(len(d), len(dn))
    print(d == dn)

    f = open("Main.json", "w")
    f.write(json.dumps(j, indent=4))
    f.close()
