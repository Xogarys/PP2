fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)
  
for i in range(1, 6):
    if i == 3:
        continue
    print(i)


for i in range(1, 7):
    if i % 2 != 0:
        continue
    print(i)


words = ["cat", "skip", "dog", "bird"]

for word in words:
    if word == "skip":
        continue
    print(word)


numbers = [1, -2, 3, -4, 5]

for n in numbers:
    if n < 0:
        continue
    print(n)
