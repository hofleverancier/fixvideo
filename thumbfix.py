import os
import subprocess
import sys
import shutil

def process_video(video_path, output_directory, delete_original, verbose=False):
    # Remove lingering thumbnail.jpg files if present
    temp_jpeg_path = 'thumbnail.jpg'
    if os.path.exists(temp_jpeg_path):
        os.remove(temp_jpeg_path)

    # Extract temporary JPEG
    extract_command = [
        'ffmpeg', '-y', '-ss', '30', '-i', video_path, '-vf', "scale='trunc(ih*dar):ih',setsar=1/1",
        '-frames:v', '1', '-q:v', '2', temp_jpeg_path
    ]
    extract_process = subprocess.run(extract_command, capture_output=True, text=False)

    if extract_process.returncode != 0:
        # Extraction failed, copy the original file with '_tf-failed' suffix
        output_filename = os.path.basename(video_path)
        output_filename = os.path.splitext(output_filename)[0] + '_tf-failed' + os.path.splitext(output_filename)[1]
        output_path = os.path.join(output_directory, output_filename)
        shutil.copy2(video_path, output_path)
        print(f"Extraction failed for {video_path}. Copied original file to {output_path} with '_tf-failed' suffix.")
        return

    # Create output directory structure
    relative_path = os.path.relpath(video_path, sys.argv[1])
    output_subdir = os.path.dirname(relative_path)
    output_subdir_path = os.path.join(output_directory, output_subdir)
    os.makedirs(output_subdir_path, exist_ok=True)

    # Embed temporary JPEG as metadata
    output_filename = os.path.basename(video_path)
    output_filename = os.path.splitext(output_filename)[0] + '_tf' + os.path.splitext(output_filename)[1]
    output_path = os.path.join(output_subdir_path, output_filename)

    embed_command = [
        'ffmpeg', '-y', '-i', video_path, '-i', temp_jpeg_path, '-map', '0', '-map', '1',
        '-c', 'copy', '-disposition:v:1', 'attached_pic', output_path
    ]
    embed_process = subprocess.run(embed_command, capture_output=True, text=False)

    if embed_process.returncode != 0:
        # Embedding failed, copy the original file with '_tf-failed' suffix
        output_filename = os.path.basename(video_path)
        output_filename = os.path.splitext(output_filename)[0] + '_tf-failed' + os.path.splitext(output_filename)[1]
        output_path = os.path.join(output_subdir_path, output_filename)
        shutil.copy2(video_path, output_path)
        print(f"Embedding failed for {video_path}. Copied original file to {output_path} with '_tf-failed' suffix.")
        return

    # Delete temporary JPEG
    os.remove(temp_jpeg_path)

    if delete_original:
        # Delete original file
        os.remove(video_path)
        print(f"Deleted original file: {video_path}")

    if verbose:
        stdout = embed_process.stdout.decode('utf-8')
        stderr = embed_process.stderr.decode('utf-8')
        print(stdout)
        print(stderr)

def process_directory(input_directory, output_directory, delete_original, verbose=False):
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mkv')) and '_tf' not in file:
                video_path = os.path.join(root, file)
                print(f"Processing: {video_path}")
                process_video(video_path, output_directory, delete_original, verbose)

# Check if the directory arguments are provided
if len(sys.argv) < 2 or sys.argv[1] == '--help':
    print("Usage: python script.py <input_directory> [--delete] [--verbose]")
    sys.exit(0)

# Retrieve the input directory path
input_directory = sys.argv[1]

# Set the output directory to be the same as input directory if not provided
if len(sys.argv) >= 3:
    output_directory = sys.argv[2]
else:
    output_directory = input_directory

# Check if the --delete option is provided
delete_original = '--delete' in sys.argv

# Check if the --verbose option is provided
verbose = '--verbose' in sys.argv

# Process the directory recursively
process_directory(input_directory, output_directory, delete_original, verbose)
