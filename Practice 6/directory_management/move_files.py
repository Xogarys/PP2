
import os
import shutil

# 1. Define source and destination directories
source_file = "example.txt"
destination_folder = "destination_folder"

# 2. Create destination folder if it does not exist
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)
    print("Destination folder created")

# 3. Create a sample file to move
with open(source_file, "w") as f:
    f.write("This is a sample file for moving.")

print("Sample file created")

# 4. Move the file to the destination folder
shutil.move(source_file, os.path.join(destination_folder, source_file))
print("File moved to destination folder")

# 5. Copy the file back to the current directory
shutil.copy(os.path.join(destination_folder, source_file), "copy_example.txt")
print("File copied back as copy_example.txt")

# 6. Show files in destination folder
print("\nFiles in destination folder:")
print(os.listdir(destination_folder))