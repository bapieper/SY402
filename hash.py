import os
import hashlib
import json

with open('hashes.txt','r') as h:
    last_hashes = h.read()
last_hashes = json.loads(last_hashes)

changed = []
hashes = {}
new = []
missing = []
unhashable = set(['usr','dev','proc','run','sys','tmp','/var/lib','/var/run'])
buf_size = 65536
sha256 = hashlib.sha256()
for dirs, subdirs, files in os.walk('/'):
    subdirs[:] = [d for d in subdirs if d not in unhashable]
    subdirs[:] = [d for d in subdirs if os.path.join(dirs,d) not in unhashable]
    file_hashes = {}
    print("Hashing: "+dirs)
    for file in files:
        try:
            fd = open(os.path.join(dirs, file),'rb')
            file_contents = fd.read(buf_size)
            sha256.update(file_contents)
            file_hashes[file] = sha256.hexdigest()
            fd.close()
        except FileNotFoundError:
            continue
        except PermissionError:
            continue
        hashes[dirs] = file_hashes
        if file not in last_hashes[dirs].keys():
            new.append(os.path.join(dirs,file))
            continue
        if hashes[dirs][file] != last_hashes[dirs][file]:
            changed.append(os.path.join(dirs,file))
            continue
    if dirs in last_hashes.keys(): 
        for key in last_hashes[dirs].keys():
            if dirs in hashes.keys():
                if key not in hashes[dirs].keys():
                    missing.append(os.path.join(dirs,key))

with open('hashes.txt','w') as hashfile:
    hashfile.write(json.dumps(hashes))

if len(new) > 0:
    print("New Files: ")
    print(new)
if len(missing) > 0:
    print("Missing Files: ")
    print(missing)
if len(changed) > 0:
    print("Changed Files: ")
    print(changed)
