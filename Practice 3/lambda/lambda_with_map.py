numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))  # multiply each number by 2
print(doubled)


# Example 2: add 1 to each number
numbers = [5, 10, 15]

plus_one = list(map(lambda x: x + 1, numbers))  # add 1 to each number
print(plus_one)


# Example 3: convert numbers to strings
numbers = [1, 2, 3]

strings = list(map(lambda x: str(x), numbers))  # convert to string
print(strings)



# Example 4: get length of each word
words = ["apple", "pie", "banana"]

lengths = list(map(lambda x: len(x), words))  # get word length
print(lengths)
