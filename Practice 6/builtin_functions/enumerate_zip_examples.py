# Example 1: Using enumerate() to get index and value from a list

names = ["Ali", "Dana", "Aruzhan"]

# enumerate() returns both index and value
for index, name in enumerate(names):
    print(index, name)


# Example 2: Using enumerate() with a starting index

fruits = ["apple", "banana", "orange"]

# start=1 makes counting begin from 1 instead of 0
for index, fruit in enumerate(fruits, start=1):
    print(index, fruit)


# Example 3: Using zip() to combine two lists

students = ["Ali", "Dana", "Aruzhan"]
scores = [90, 85, 95]

# zip() pairs elements from both lists together
for student, score in zip(students, scores):
    print(student, score)


# Example 4: Using zip() to combine three lists

names = ["Ali", "Dana", "Aruzhan"]
ages = [18, 19, 20]
cities = ["Almaty", "Astana", "Shymkent"]

# zip() combines elements with the same index
for name, age, city in zip(names, ages, cities):
    print(name, age, city)