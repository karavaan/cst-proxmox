import subprocess
import re

vm_list = []

result = subprocess.run(['qm', 'list'], stdout=subprocess.PIPE)
result.stdout

extracted = re.findall("\d{3}", str(result))

f = open("tempList.txt", "w")

for x in extracted:
    result2 = subprocess.run(['qm', 'guest', 'cmd', x, 'network-get-interfaces'], stdout=subprocess.PIPE)

    if re.findall("(?:[0-9]{1,3}\.){3}[0-9]{1,3}", str(result2)):

        f.write(x)
        f.write(str(re.findall("(?:[0-9]{1,3}\.){3}[0-9]{1,3}", str(result2))))
        f.write("\n")
    
f = open("tempList.txt", "r")
print(f.read())