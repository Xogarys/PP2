fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break

fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    break
  print(x)
  
for x in range(6):
  if x == 3: break
  print(x)
else:
  print("Finally finished!")
  
for i in range(1, 11):
    if i == 5:
        break
    print(i)


numbers = [1, 3, 5, 7, 9]

for n in numbers:
    if n == 5:
        break
    print(n)


passwords = ["123", "admin", "python", "qwerty"]

for p in passwords:
    if p == "python":
        print("Access granted")
        break


nums = [5, 4, 3, -1, 2]

for n in nums:
    if n < 0:
        break
    print(n)
