# Example 1: Open a file and read the entire content

f = open("demofile.txt")  # Open the file in read mode (default)
print(f.read())           # Read and print the whole file


# Example 2: Using "with" statement to open and read a file
# The file will be automatically closed after the block

with open("sample.txt", "r") as f:
    content = f.read()    # Read all text from the file

print(content)            # Print the content


# Example 3: Open a file using an absolute path

f = open("D:\\myfiles\\welcome.txt")  # Use double backslashes in Windows paths
print(f.read())                       # Print the file content


# Example 4: Using "with" to open a file (default mode is read)

with open("demofile.txt") as f:
    print(f.read())      # Read and print the file


# Example 5: Read only the first line of the file

f = open("demofile.txt")
print(f.readline())      # Read the first line
f.close()                # Close the file manually


# Example 6: Read the first line using "with"

with open("demofile.txt") as f:
    print(f.readline())  # Read and print one line


# Example 7: Read the file line by line using a loop

with open("demofile.txt") as f:
    for x in f:          # Loop through each line in the file
        print(x)         # Print each line