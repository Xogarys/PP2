import os

# 1. Show the current working directory
current_directory = os.getcwd()
print("Current directory:", current_directory)

# 2. Create a single folder
folder_name = "example_folder"

# 3. Create nested directories
nested_path = "example_folder/subfolder1/subfolder2"

# Check if nested directories exist before creating them
if not os.path.exists(nested_path):
    os.makedirs(nested_path)
    print("Nested directories created:", nested_path)
else:
    print("Nested directories already exist")

# 4. List all files and folders in the current directory
print("\nFiles and directories in the current folder:")
items = os.listdir()

for item in items:
    print(item)

# 5. Change the working directory
os.chdir("example_folder")
print("\nChanged directory to:", os.getcwd())

# 6. Show contents of the new directory
print("\nContents of example_folder:")
print(os.listdir())