i = 0
while i < 6:
  i += 1
  if i == 3:
    continue
  print(i)
  
i = 1

while i <= 5:
    if i == 3:
        i += 1
        continue
    print(i)
    i += 1


i = 1

while i <= 6:
    if i % 2 != 0:
        i += 1
        continue
    print(i)
    i += 1


words = ["cat", "dog", "skip", "bird"]
i = 0

while i < len(words):
    if words[i] == "skip":
        i += 1
        continue
    print(words[i])
    i += 1


