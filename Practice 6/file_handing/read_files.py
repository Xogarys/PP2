f = open("demofile.txt")
print(f.read())



with open("sample.txt", "r") as f:
    content = f.read()

print(content)


f = open("D:\\myfiles\welcome.txt")
print(f.read())

with open("demofile.txt") as f:
  print(f.read())
  
f = open("demofile.txt")
print(f.readline())
f.close()

with open("demofile.txt") as f:
  print(f.readline())
  
  
with open("demofile.txt") as f:
  for x in f:
    print(x)
