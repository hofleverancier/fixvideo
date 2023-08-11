import os
import subprocess
import sys
import shutil

def process_folder(folder_path, output_folder):
    # Get a list of all files and subfolders in the folder
    files = []
    subfolders = []
    for entry in os.scandir(folder_path):
        if entry.is_file():
            files.append(entry.name)
        elif entry.is_dir():
            subfolders.append(entry.name)

    # List of video file extensions
    video_extensions = ['.avi', '.mp4', '.wmv']

    total_files = 0
    processed_files = 0

    # Recreate the folder structure in the output folder if provided
    if output_folder:
        recreate_folder_structure(folder_path, output_folder)

    for file_name in files:
        # Check if the file has a video extension
        if any(file_name.lower().endswith(ext) for ext in video_extensions):
            total_files += 1
            file_path = os.path.join(folder_path, file_name)
            fixed_file_path = generate_fixed_file_path(file_path, output_folder)

            # Execute the ffmpeg command on the video file
            command = f'ffmpeg -v error -i "{file_path}" -ignore_unknown -c copy "{fixed_file_path}"'
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for the process to finish and get the output
            output, error = process.communicate()

            # Print any errors encountered during execution
            if error:
                print(f"Error processing file: {file_path}")
                print(error.decode("utf-8"))
            else:
                processed_files += 1
                print(f"Processed file: {file_path}")

    for subfolder_name in subfolders:
        subfolder_path = os.path.join(folder_path, subfolder_name)
        subfolder_output_path = None
        if output_folder:
            subfolder_output_path = os.path.join(output_folder, subfolder_name)
            os.makedirs(subfolder_output_path, exist_ok=True)

        process_folder(subfolder_path, subfolder_output_path)

    print(f"Total files: {total_files}")
    print(f"Processed files: {processed_files}")

def recreate_folder_structure(folder_path, output_folder):
    # Get the relative path of the folder from the root folder
    relative_path = os.path.relpath(folder_path, start=os.path.dirname(folder_path))

    # Create the corresponding folder in the output folder
    recreated_folder = os.path.join(output_folder, relative_path)
    os.makedirs(recreated_folder, exist_ok=True)

def generate_fixed_file_path(file_path, output_folder):
    # Get the file name and extension
    file_base_name, file_extension = os.path.splitext(os.path.basename(file_path))

    if output_folder:
        # Generate the fixed file path in the specified output folder
        fixed_file_path = os.path.join(output_folder, f"{file_base_name}_fixed{file_extension}")
    else:
        # Generate the fixed file path in the same folder as the original file
        fixed_file_path = os.path.join(os.path.dirname(file_path), f"{file_base_name}_fixed{file_extension}")

    # Check if the file already exists in the target folder
    counter = 1
    while os.path.exists(fixed_file_path):
        fixed_file_path = os.path.join(output_folder, f"{file_base_name}_fixed({counter}){file_extension}")
        counter += 1

    return fixed_file_path

def print_help():
    print("Usage: python video_fixer.py [path] [options]")
    print("Options:")
    print("  --output-folder <folder> : Specify the output folder for fixed files")
    print("  --recursive              : Process files in the specified folder and its subfolders recursively")
    print("  --help                   : Show this help message")
    print()
    print("Description:")
    print("This script processes video files in the specified path or folder and fixes")
    print("them using the 'ffmpeg' command. It creates fixed versions of the video files")
    print("with the same name but appended with '_fixed'. The fixed files are placed")
    print("in the specified output folder.")
    print()
    print("Examples:")
    print("  python video_fixer.py video.mp4 --output-folder fixed_videos")
    print("  python video_fixer.py /path/to/videos --output-folder /path/to/fixed_videos")
    print("  python video_fixer.py /path/to/videos --output-folder /path/to/fixed_videos --recursive")

if __name__ == '__main__':
    # Check if the path is provided as an argument
    if len(sys.argv) < 2:
        print("Please provide the folder path or file path as an argument.")
        sys.exit(1)

    path = sys.argv[1]

    if path.lower() == "--help":
        print_help()
        sys.exit(0)

    output_folder = None
    recursive = False

    if len(sys.argv) >= 3:
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i].lower()

            if arg == '--output-folder' and i + 1 < len(sys.argv):
                output_folder = sys.argv[i + 1]
                i += 1
            elif arg == '--recursive':
                recursive = True
            elif arg == '--help':
                print_help()
                sys.exit(0)
            else:
                print("Invalid option. Use '--help' to see the available options.")
                sys.exit(1)

            i += 1

    if recursive and not output_folder:
        print("Please provide an output folder when using the '--recursive' option.")
        sys.exit(1)

    process_folder(path, output_folder)
