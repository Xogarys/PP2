# Example 1: Using map() to apply a function to every element in a list

numbers = [1, 2, 3, 4]

# map() applies the function (lambda x: x*x) to each element in the list
# This will calculate the square of each number
squares = list(map(lambda x: x * x, numbers))

# Print the new list with squared values
print(squares)



# Example 2: Using filter() to select specific elements from a list

numbers = [1, 2, 3, 4, 5, 6]

# filter() keeps only elements where the condition is True
# Here we keep only even numbers (numbers divisible by 2)
even = list(filter(lambda x: x % 2 == 0, numbers))

# Print the list of even numbers
print(even)



# Example 3: Using reduce() to combine all elements into a single value

from functools import reduce

numbers = [1, 2, 3, 4]

# reduce() applies the function cumulatively to the elements
# It adds numbers together: ((1+2)+3)+4
total = reduce(lambda x, y: x + y, numbers)

# Print the sum of all numbers
print(total)