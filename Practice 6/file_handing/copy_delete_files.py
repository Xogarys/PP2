import os

# Delete a file named "demofile.txt"
# If the file exists, it will be removed from the directory
os.remove("demofile.txt")


import os

# Check if the file exists before deleting it
# This prevents an error if the file is not found
if os.path.exists("demofile.txt"):
    os.remove("demofile.txt")  # Remove the file
else:
    print("The file does not exist")  # Print message if file is missing


import os

# Remove an empty directory named "myfolder"
# Note: os.rmdir() only works if the folder is empty
os.rmdir("myfolder")


import shutil

# Copy the file "sample.txt" to a new file named "backup.txt"
# The original file remains unchanged
shutil.copy("sample.txt", "backup.txt")