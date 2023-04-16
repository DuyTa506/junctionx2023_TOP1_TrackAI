#LOCKED
import os
from temp import infer
import time
tic = time.time()
def get_files(root_dir):
    files = []
    for subdir, dirs, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(subdir, filename)
            files.append(file_path)
    return files

def get_subdirectories(root_dir):
    subdirectories = []
    for dir_name in os.listdir(root_dir):
        dir_path = os.path.join(root_dir, dir_name)
        if os.path.isdir(dir_path):
            subdirectories.append(dir_path)
    return subdirectories

# Example usage:
root_dir = "match_vid/Public_Test/test"
subdirs = get_subdirectories(root_dir)
for item in subdirs:
    infer(item)

tac = time.time()
print((tac - tic)* 1000)
    
