numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))  # keep only odd numbers
print(odd_numbers)

# keep positive numbers
numbers = [-3, -1, 0, 2, 5, -7]

positive_numbers = list(filter(lambda x: x > 0, numbers))  # keep positive numbers
print(positive_numbers)

# keep numbers greater than 5
numbers = [2, 4, 6, 8, 3, 5, 9]

big_numbers = list(filter(lambda x: x > 5, numbers))  # keep numbers > 5
print(big_numbers)
