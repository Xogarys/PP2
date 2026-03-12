import re

# 1
pattern = r"ab*"   # 'a' followed by zero or more 'b'
text = "abbb"
# re.fullmatch checks if the whole string matches the pattern
if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")


# 2
pattern = r"ab{2,3}"   # 'a' followed by 2 or 3 'b'
text = "ab"
# {2,3} means the previous character must appear from 2 to 3 times
if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")


# 3
pattern = r"[a-z]+_[a-z]+"
# [a-z]+  -> one or more lowercase letters
# _       -> underscore symbol
# [a-z]+  -> one or more lowercase letters again

text = "hello_world test_case anotherExample"

# findall returns all matches found in the string
result = re.findall(pattern, text)

print(result)


# 4
pattern = r"[A-Z][a-z]+"
# [A-Z]   -> one uppercase letter
# [a-z]+  -> one or more lowercase letters

text = "Hello world Python Code"

# this finds words like "Hello", "Python", "Code"
result = re.findall(pattern, text)

print(result)


# 5
pattern = r"a.*b"
# a   -> string starts with 'a'
# .*  -> any characters (0 or more)
# b   -> ends with 'b'

text = "axxxbс"

if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")


# 6
text = "Hello, world. Python is fun"

# [ ,\.] means: space OR comma OR dot
# re.sub replaces all matches with ":"
result = re.sub(r"[ ,\.]", ":", text)

print(result)


# 7
def snake_to_camel(text):
    # split string by underscore
    parts = text.split('_')

    # first word stays lowercase
    # next words start with uppercase using capitalize()
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

print(snake_to_camel("hello_world_python"))


# 8
text = "HelloWorldPython"

# (?=[A-Z]) is a lookahead
# it splits the string BEFORE every uppercase letter
result = re.split(r"(?=[A-Z])", text)

print(result)


# 9
text = "HelloWorldPython"

# ([A-Z]) finds every uppercase letter
# r" \1" adds a space before that letter
result = re.sub(r"([A-Z])", r" \1", text).strip()

# strip() removes the space at the beginning
print(result)


# 10
def camel_to_snake(text):

    # ([A-Z]) finds uppercase letters
    # _\1 adds underscore before them
    result = re.sub(r'([A-Z])', r'_\1', text)

    # convert everything to lowercase
    # lstrip('_') removes underscore at the beginning
    return result.lower().lstrip('_')

print(camel_to_snake("HelloWorldPython"))