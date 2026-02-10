students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])  # sort by age (2nd item)
print(sorted_students)


words = ["apple", "pie", "banana", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))  # sort by word length
print(sorted_words)

students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])  # sort by age (2nd item)
print(sorted_students)


words = ["apple", "pie", "banana", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))  # sort by word length
print(sorted_words)


# Example 4: sort students by name
students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]

sorted_by_name = sorted(students, key=lambda x: x[0])  # sort by name
print(sorted_by_name)
