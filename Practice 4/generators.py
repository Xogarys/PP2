def squares(n):
    for i in range(n + 1):
        yield i * i

# Example
for value in squares(5):
    print(value)



def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input("Enter n: "))

print(",".join(str(num) for num in even_numbers(n)))




def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

# Example
for num in divisible_by_3_and_4(50):
    print(num)






def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

# Test
for value in squares(3, 7):
    print(value)


