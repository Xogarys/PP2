# "r" - Read - Default value. Opens a file for reading, error if the file does not exist

# "a" - Append - Opens a file for appending, creates the file if it does not exist

# "w" - Write - Opens a file for writing, creates the file if it does not exist

# "x" - Create - Creates the specified file, returns an error if the file exists

# "t" - Text - Default value. Text mode

# "b" - Binary - Binary mode (e.g. images)

# Example 1: Writing data to a file using write mode ("w")

# "w" mode creates a new file or overwrites the file if it already exists
with open("sample.txt", "w") as f:
    f.write("Hello\n")                 # Write the first line
    f.write("This is practice 6\n")    # Write the second line


# Example 2: Appending new content to an existing file using append mode ("a")

# "a" mode adds new content to the end of the file without deleting existing data
with open("demofile.txt", "a") as f:
    f.write("Now the file has more content!")


# Open and read the file after appending
with open("demofile.txt") as f:
    print(f.read())   # Print the file content


# Example 3: Overwriting the file using write mode ("w")

# This will delete the old content and replace it with new text
with open("demofile.txt", "w") as f:
    f.write("Woops! I have deleted the content!")


# Open and read the file after overwriting
with open("demofile.txt") as f:
    print(f.read())   # Print the new content