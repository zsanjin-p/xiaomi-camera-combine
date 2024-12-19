# Xiaomi Camera Combination
xiaomicameracombine is a surveillance video tool that merges Xiaomi cameras in SD card and NAS

I use Xiaomi PTZ 2, which is set to real-time synchronization. Generally, one video is saved per minute and then synchronized to NAS. For cyber obsessive-compulsive disorder, I want to merge these videos, which is also convenient for future use.

Tested in Synology 7.2, virtual python38 environment, and theoretically there is no problem with Windows.

The directory structure of Xiaomi PTZ 2, v5.1.6_0397 may change with the version upgrade, but it is generally like this
Other models of Xiaomi surveillance cameras may be useful, but not necessarily.
Other brands of monitoring can be used, but I think only Xiaomi can export to NAS cloud for storage

<p alignment="center">
<img src="https://github.com/user-attachments/assets/2518063a-d85b-4ee9-a2a5-b9188184adae" width="500" height="500">
</p>

## File directory structure
monitor/                                       # Monitoring root directory (MONITOR_PATH)
├── 2024121723/                                # Time folder (23:00, December 17, 2024)
│ ├── 35M26S_1734443966.mp4                    # Video file (recording starts at 35 minutes and 26 seconds)
│ ├── 36M26S_1734443967.mp4
│ └── 37M26S_1734443968.mp4
├── 2024121800/                                # 2024 December 18, 00:00
│ ├── 01M26S_1734443969.mp4
│ ├── 02M26S_1734443970.mp4
│ └── 03M26S_1734443971.mp4
└── 2024121801/                                # 2024 December 18, 01:00
├── 15M26S_1734443972.mp4
├── 16M26S_1734443973.mp4
└── 17M26S_1734443974.mp4

Combined Video/                                #Output directory (OUTPUT_PATH)
├── 2024-1217-23-35M26S-->2024-1217-23-37M26S.mp4 # Merged video
└── 2024-1218-00-01M26S-->2024-1218-00-03M26S.mp4

log/                                           # Log directory
├── General log.log
└── 2024-12-18_000123-->2024-1217-23-35M26S-->2024-1217-23-37M26S.mp4.log

fliedata/                                      # Data directory
└── File-202412180001.json # Database file

Key points:

1. The video source folder must be in the YYYYMMDDHH format (such as: 2024121723)

2. The video file is recommended to use the format: minutes M seconds S_timer.mp4 (such as: 35M26S_1734443966.mp4)

3. The merged video file name will be automatically generated, including the start and end time information

4. The program will automatically create the required directories (CombineVideo, log, fliedata)

### So as long as the root directory of your video source folder saves the video in the folder name format of YYYYMMDDHH, you can use this tool

## Environment variables

The root directory of surveillance video, which is the directory synchronized to nas

MONITOR_PATH=/volume1/xiaomicamera/xiaomi_camera_videos/78HJK888839

The number of merges each time, the default value is 60, one video is one minute

COMBINE_DURATION=

Whether to delete the source video, Y or N is optional

The default is N, do not delete, data is priceless, delete with caution

DELETE_SOURCE=N

The storage path of the merged video, the default is in the working directory, it is not recommended to put it in the video source folder, I don’t know what will happen

OUTPUT_PATH=./CombineVideo

Whether to run the program in a loop, Y or N, the default is N

If you choose Y, it will run until all videos within the COMBINE_DURATION value are merged and exit

It is recommended to set it to Y, and then arrange a scheduled task to run regularly

LOOP=N

FFmpeg Path to the executable file. The system's own version may not run. I use FFmpeg version 7.x
FFMPEG_PATH=/volume1/nasuser/xiaomicamera/ffmpeg/ffmpeg

Video compression options (optional values: 0-10)
0 represents direct splicing without compression, 1 represents the lowest level of compression, high quality, 10 represents the highest level of compression, low quality
COMPRESS_VIDEO=10

## How to use

1. Download the repository file
```
git clone https://github.com/zsanjin-p/xiaomi-camera-combine
```
3. Install python3 or above
4. Install the pyhton virtual environment
```
#You can replace dateutil_env with other names
python -m venv dateutil_env
cd dateutil_env /
source bin/activate
```
6. Install the third-party library that loads environment variables after activation
```
pip install python-dotenv
```
7. Set the environment variables of the .env file, especially the monitoring source file directory, otherwise it will not run
8. Run the program. Note that if it is a small garbage, it will run very slowly. Please wait patiently or run it during the NAS idle period
```
python xiaomi-camera-combine.py
```
9. You can run it regularly with the task plan

### If there are too many videos and I don't want to merge them from scratch, what should I do?

tips: Create a file named: last_processed.json in the working directory of this tool. The file content format is as follows:
```
{"last_folder": "2024121412", "last_video": "20M50S_1734150050.mp4"}
```
Where 2024121412 is the file where the video is saved, and 20M50S_1734150050.mp4 is the video file in the folder. This file represents that this is the last video merged last time.
By modifying this file, you can set the starting point of the splicing.

## Contribution

If you like this project, please consider giving us a star! ⭐⭐⭐
