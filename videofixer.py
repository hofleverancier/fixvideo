import argparse
import os
import subprocess
import shutil

def fix_video(input_file, output_file, delete=False):
    try:
        subprocess.check_output(['ffmpeg', '-i', input_file, '-c', 'copy', '-map', '0', '-y', output_file])
        output_file_fixed = os.path.splitext(output_file)[0] + '_fixed' + os.path.splitext(output_file)[1]
        count = 1
        while os.path.exists(output_file_fixed):
            output_file_fixed = f"{os.path.splitext(output_file)[0]}_fixed_{count}{os.path.splitext(output_file)[1]}"
            count += 1
        if input_file != output_file_fixed:
            os.rename(output_file, output_file_fixed)
            if delete:
                os.remove(input_file)
                print(f'Success (Deleted): {input_file}')
            else:
                print(f'Success: {input_file}')
    except subprocess.CalledProcessError as e:
        print(f'Failed: {input_file}')
        os.rename(input_file, output_file)


def fix_videos(input_folder, output_folder, recursive=False, delete=False):
    os.makedirs(output_folder, exist_ok=True)

    for root, dirs, files in os.walk(input_folder):
        if not recursive:
            dirs.clear()  # Prevent descending into subdirectories

        for file in files:
            input_file = os.path.join(root, file)
            output_file = os.path.join(output_folder, os.path.relpath(input_file, input_folder))
            output_dir = os.path.dirname(output_file)
            os.makedirs(output_dir, exist_ok=True)
            fix_video(input_file, output_file, delete=delete)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video Fixer')
    parser.add_argument('input_folder', help='Input folder')
    parser.add_argument('output_folder', help='Output folder')
    parser.add_argument('--recursive', '-r', action='store_true', help='Enable recursive mode')
    parser.add_argument('--delete', '-d', action='store_true', help='Delete successfully processed files')

    args = parser.parse_args()
    fix_videos(args.input_folder, args.output_folder, args.recursive, args.delete)
