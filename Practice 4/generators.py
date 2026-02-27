# Task 1: Generate squares of numbers from 0 to n
def squares(n):
    for i in range(n + 1):
        yield i * i          # Yield the square of each number one by one

# Example: print squares from 0 to 5
for value in squares(5):
    print(value)


# Task 2: Generate even numbers from 0 to n
def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:       # Check if the number is divisible by 2 (even)
            yield i

# Ask the user for input and print all even numbers separated by commas
n = int(input("Enter n: "))
print(",".join(str(num) for num in even_numbers(n)))


# Task 3: Generate numbers divisible by both 3 and 4 (i.e. divisible by 12)
def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:  # Number must satisfy both conditions
            yield i

# find all such numbers from 0 to 50
for num in divisible_by_3_and_4(50):
    print(num)


# Task 4: Generate squares of numbers in a given range [a, b]
def squares(a, b):
    for i in range(a, b + 1):   # Start from a, end at b (inclusive)
        yield i * i              # Yield the square of each number

#  print squares of numbers from 3 to 7
for value in squares(3, 7):
    print(value)
