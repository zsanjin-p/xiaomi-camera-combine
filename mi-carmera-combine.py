# -*- coding: utf-8 -*-

import os
import json
import time
import sys
from datetime import datetime
from pathlib import Path
import subprocess

# Load environment variables
# 加载环境变量
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment variables
# 从环境变量加载配置
MONITOR_PATH = os.getenv("MONITOR_PATH", "./monitor")
COMBINE_DURATION = int(os.getenv("COMBINE_DURATION", 60))
DELETE_SOURCE = os.getenv("DELETE_SOURCE", "N").upper() == "Y"
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./CombineVideo")
LOOP = os.getenv("LOOP", "N").upper() == "Y"
COMPRESS_VIDEO = int(os.getenv("COMPRESS_VIDEO", "0")) 

# Select default FFmpeg path based on operating system
# 根据操作系统选择默认的 FFmpeg 路径
if sys.platform.startswith('win'):
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg.exe")
else:
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

data_dir = Path("fliedata")
data_dir.mkdir(exist_ok=True)

# JSON database path
# JSON 数据库路径
json_file_path = data_dir / f"File-{datetime.now().strftime('%Y%m%d%H%M')}.json"

# Ensure output directory exists
# 确保输出目录存在
output_dir = Path(OUTPUT_PATH)
output_dir.mkdir(exist_ok=True)

# Initialize logger
# 初始化日志系统
log_dir = Path("log")
log_dir.mkdir(exist_ok=True)


# Temporary log file (general log for current run)
# 临时日志文件（当前运行的通用日志）
general_log_file = log_dir / "general_log.log"

# Global log file (to be updated dynamically)
# 全局日志文件（动态更新）
global_log_file = None


def set_log_file(output_file_name):
    """
    Set the global log file name based on the output video file name
    根据输出视频文件名设置全局日志文件名
    """
    global global_log_file
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    global_log_file = log_dir / f"{run_timestamp}-->{output_file_name}.log"


def log(message):
    """
    Write messages to both the general log and the global log file
    将消息同时写入通用日志和全局日志文件
    """
    with open(general_log_file, "a", encoding="utf-8") as logf:
        logf.write(f"{datetime.now()}: {message}\n")
    if global_log_file:
        with open(global_log_file, "a", encoding="utf-8") as logf:
            logf.write(f"{datetime.now()}: {message}\n")
    print(message)
    
def finalize_logs():
    """
    Finalize and merge log files
    完成并合并日志文件
    """
    if global_log_file:
        # Append contents of general_log to the global log file
        # 将通用日志内容附加到全局日志文件
        with open(general_log_file, "r", encoding="utf-8") as gen_log:
            general_log_content = gen_log.read()
        with open(global_log_file, "a", encoding="utf-8") as final_log:
            final_log.write("\n--- General Log Start ---\n")
            final_log.write(general_log_content)
            final_log.write("\n--- General Log End ---\n")
        print(f"General log merged into: {global_log_file}")

    # Clear the general log for the next run
    # 清空通用日志以供下次运行使用
    open(general_log_file, "w").close()


def get_sorted_folders(path):
    """
    Get and validate folders in chronological order
    获取并验证按时间顺序排序的文件夹
    """
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    valid_folders = []

    for folder in folders:
        try:
            datetime.strptime(folder, "%Y%m%d%H")  # Validate folder name format
            valid_folders.append(folder)
            log(f"Valid folder: {folder}")
        except ValueError:
            log(f"Ignored invalid folder: {folder}")

    sorted_folders = sorted(valid_folders)
    log(f"Sorted folders: {sorted_folders}")
    return sorted_folders


def build_json_database():
    """
    Build JSON database for video processing
    构建视频处理的 JSON 数据库
    """
    sorted_folders = get_sorted_folders(MONITOR_PATH)
    database = {}
    absolute_video_counter = 0

    for index, folder in enumerate(sorted_folders):
        folder_path = Path(MONITOR_PATH) / folder
        videos = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]
        videos.sort()  # Sort videos in ascending order

        folder_data = {
            "sort_index": f"{index+1:010}",
            "folder_name": folder,
            "videos": []
        }
        log(f"Processing folder: {folder} (sort index: {index + 1})")

        for video_index, video in enumerate(videos):
            absolute_video_counter += 1
            video_data = {
                "video_sort_index": f"{video_index+1:010}",
                "video_name": video,
                "absolute_sort_index": f"{absolute_video_counter:011}",
                "absolute_path": str(folder_path / video),
                "folder_name": folder
            }
            folder_data["videos"].append(video_data)

        database[folder] = folder_data

    # Save to JSON file
    with open(json_file_path, "w") as json_file:
        json.dump(database, json_file, indent=4)

    log(f"JSON database successfully created: {json_file_path}")


def load_json_database():
    """
    Load JSON database from file
    从文件加载 JSON 数据库
    """
    with open(json_file_path, "r") as json_file:
        log("JSON database loaded successfully.")
        return json.load(json_file)


def get_next_batch_to_process():
    """
    Get the starting point for the next batch of videos to process
    获取下一批要处理的视频的起始点
    """
    log_file = Path("last_processed.json")

    if log_file.exists():
        try:
            with open(log_file, "r") as logf:
                last_processed = json.load(logf)

            last_folder = last_processed.get("last_folder")
            last_video = last_processed.get("last_video")

            database = load_json_database()

            found = False
            start_index = 0
            for folder_name, folder_data in database.items():
                if folder_name == last_folder:
                    found = True
                    for video in folder_data["videos"]:
                        if video["video_name"] == last_video:
                            start_index = int(video["absolute_sort_index"]) + 1
                            break
                    if found:
                        break

            if not found:
                log("Last processed file not found in database. Starting from scratch.")
                return 0

            log(f"Resuming from folder: {last_folder}, video: {last_video}")
            return start_index
        except (json.JSONDecodeError, KeyError):
            log("Error reading last_processed.json. Starting from scratch.")
            return 0
    else:
        log("No previous processing log found. Starting from scratch.")
        return 0


def get_ffmpeg_merge_command(temp_file_list, output_file):
    """
    Generate FFmpeg command for video merging with compression options
    生成带有压缩选项的 FFmpeg 视频合并命令
    """
    base_command = [
        FFMPEG_PATH, "-f", "concat", "-safe", "0", "-i", str(temp_file_list)
    ]

    if COMPRESS_VIDEO == 0:
        # Direct copy without compression
        # 不压缩，直接复制
        base_command += ["-c:v", "copy", "-c:a", "copy"]
    else:
        # Compression settings based on level 1-10
        # 基于 1-10 级别的压缩设置
        crf = 17 + (COMPRESS_VIDEO - 1) * (51 - 17) // 9
        
        if COMPRESS_VIDEO <= 3:
            preset = "slow"
        elif COMPRESS_VIDEO <= 7:
            preset = "medium"
        else:
            preset = "fast"

        audio_bitrate = 192 - (COMPRESS_VIDEO - 1) * 16  # 192k to 48k

        base_command += [
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-c:a", "aac",
            "-b:a", f"{audio_bitrate}k",
            "-strict", "-2"
        ]

    base_command.append(str(output_file))
    return base_command


def generate_output_filename(first_video, last_video):
    """
    Generate output filename based on first and last video information
    根据第一个和最后一个视频的信息生成输出文件名
    """
    first_folder = first_video['folder_name']
    first_video_name = first_video['video_name']
    last_folder = last_video['folder_name']
    last_video_name = last_video['video_name']
    
    def format_folder_name(folder):
        return f"{folder[:4]}-{folder[4:8]}-{folder[8:]}"
    
    def extract_minute_part(video_name):
        return video_name.split('S_')[0] + 'S'
    
    first_part = f"{format_folder_name(first_folder)}-{extract_minute_part(first_video_name)}"
    last_part = f"{format_folder_name(last_folder)}-{extract_minute_part(last_video_name)}"
    
    return f"{first_part}-->{last_part}.mp4"


def process_batch(start_index):
    """
    Process a batch of videos for combining
    处理一批要合并的视频
    """
    database = load_json_database()
    videos_to_merge = []

    for folder_name, folder_data in database.items():
        for video in folder_data["videos"]:
            if int(video["absolute_sort_index"]) >= start_index and len(videos_to_merge) < COMBINE_DURATION:
                videos_to_merge.append(video)

    if not videos_to_merge:
        log("No more videos to process. Exiting.")
        return False, start_index

    temp_file_list = Path("temp_file_list.txt")
    with open(temp_file_list, "w") as temp_file:
        for video in videos_to_merge:
            temp_file.write(f"file '{video['absolute_path']}'\n")

    first_video = videos_to_merge[0]
    last_video = videos_to_merge[-1]
    output_file_name = generate_output_filename(first_video, last_video)
    output_file = output_dir / output_file_name

    set_log_file(output_file_name)

    merge_command = get_ffmpeg_merge_command(temp_file_list, output_file)

    try:
        subprocess.run(merge_command, check=True)

        log(f"Merged videos to: {output_file}")

        with open("last_processed.json", "w") as logf:
            json.dump({
                "last_folder": videos_to_merge[-1]["folder_name"],
                "last_video": videos_to_merge[-1]["video_name"]
            }, logf)

        if DELETE_SOURCE:
            for video in videos_to_merge:
                os.remove(video["absolute_path"])
                log(f"Deleted source video: {video['absolute_path']}")

        if temp_file_list.exists():
            temp_file_list.unlink()
            
        next_start_index = int(videos_to_merge[-1]["absolute_sort_index"]) + 1
    except subprocess.CalledProcessError as e:
        log(f"Failed to merge videos: {e}")
        return False, start_index
        
    return True, next_start_index


def main():
    """
    Main function to run the video combining process
    运行视频合并处理的主函数
    """
    log("Program started.")
    build_json_database()
    start_index = get_next_batch_to_process()

    while True:
        success, next_index = process_batch(start_index)
        if not success or not LOOP:
            log("Processing completed. Exiting program.")
            break
        start_index = next_index
        log(f"Starting next batch from index: {start_index}")

    finalize_logs()


if __name__ == "__main__":
    main()