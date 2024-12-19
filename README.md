# xiaomi-camera-combine
xiaomicameracombine合并小米摄像头存在在sd卡、nas的监控视频工具

我用的是小米云台2，设置的是实时同步，一般来说一分钟保存一个视频，然后同步到nas中。出于赛博强迫症，想要把这些视频合并起来，也方便日后使用。

在群晖7.2，虚拟python38环境下通过测试，windows理论上也没问题。

适配小米云台2，v5.1.6_0397的目录结构，可能随着版本升级会有变化，一般就这样了
小米其他型号监控摄像头很可能能用，但也不一定。
其他品牌监控可能能用，但是能输出到nas私有云保存的，据我所知只有小米一家吧

<p align="center">
  <img src="https://github.com/user-attachments/assets/2518063a-d85b-4ee9-a2a5-b9188184adae" width="500" height="500">
</p>



## 文件目录结构
monitor/                         # 监控根目录 (MONITOR_PATH)
├── 2024121723/                  # 时间文件夹 (2024年12月17日23时)
│   ├── 35M26S_1734443966.mp4    # 视频文件（35分26秒开始录制）
│   ├── 36M26S_1734443967.mp4
│   └── 37M26S_1734443968.mp4
├── 2024121800/                  # 2024年12月18日00时
│   ├── 01M26S_1734443969.mp4
│   ├── 02M26S_1734443970.mp4
│   └── 03M26S_1734443971.mp4
└── 2024121801/                  # 2024年12月18日01时
    ├── 15M26S_1734443972.mp4
    ├── 16M26S_1734443973.mp4
    └── 17M26S_1734443974.mp4

CombineVideo/                    # 输出目录 (OUTPUT_PATH)
├── 2024-1217-23-35M26S-->2024-1217-23-37M26S.mp4    # 合并后的视频
└── 2024-1218-00-01M26S-->2024-1218-00-03M26S.mp4

log/                             # 日志目录
├── general_log.log
└── 2024-12-18_000123-->2024-1217-23-35M26S-->2024-1217-23-37M26S.mp4.log

fliedata/                        # 数据目录
└── File-202412180001.json       # 数据库文件

关键点说明：
1. 视频源文件夹必须是 YYYYMMDDHH 格式（如：2024121723）
2. 视频文件建议使用格式：分钟M秒数S_时间戳.mp4 （如：35M26S_1734443966.mp4）
3. 合并后的视频文件名会自动生成，包含开始和结束的时间信息
4. 程序会自动创建必要的目录（CombineVideo、log、fliedata）

### 所以只要你的视频源文件夹的根目录保存视频的文件夹命名形式为YYYYMMDDHH就可以使用本工具

## 环境变量

监控录像根目录，也就是同步到nas的目录  
MONITOR_PATH=/volume1/xiaomicamera/xiaomi_camera_videos/78HJK888839

每次合并的个数，默认值60，一个视频一分钟  
COMBINE_DURATION=

是否删除源视频，Y或者N可选  
默认为N，不删除，数据无价，谨慎删除  
DELETE_SOURCE=N

合并后视频存放路径，默认在工作目录下，不建议放到视频源文件夹下，我也不知道会发生什么  
OUTPUT_PATH=./CombineVideo

是否循环运行程序，Y或N，默认N  
若选择Y会一直运行到COMBINE_DURATION值限定下的所有视频合并完成后退出  
建议设置为Y，然后安排个计划任务，定期运行  
LOOP=N

FFmpeg 可执行文件的路径，系统自带的版本低可能无法运行，我用的是7.x版本的FFmpeg  
FFMPEG_PATH=/volume1/nasuser/xiaomicamera/ffmpeg/ffmpeg

视频压缩选项（可选值：0-10）  
0代表直接拼接不压缩，1代表最低程度的压缩，画质高，10代表最高程度压缩，画质低  
COMPRESS_VIDEO=10


## 使用方式

1. 下载仓库文件
   ```
   git clone https://github.com/zsanjin-p/xiaomi-camera-combine
   ```
3. 安装python3以上版本
4. 安装pyhton虚拟环境
   ```
   #可以将dateutil_env替换为其他名字
   python -m venv dateutil_env
   cd dateutil_env /
   source bin/activate
   ```
6. 激活后安装加载环境变量的第三方库
   ```
   pip install python-dotenv
   ```
7. 设置好.env文件的环境变量，特别是监控源文件目录要设置好，否则无法运行
8. 运行程序，注意，如果是小垃圾运行会很慢，请耐心等待，或者在nas闲置期间运行
   ```
   python xiaomi-camera-combine.py
   ```
9. 可以搭配任务计划定期运行


### 如果视频太多，我不想从头开始合并，怎么办？

tips: 在本工具的工作目录下建立一个名为:last_processed.json的文件，文件内容格式如下:
```
{"last_folder": "2024121412", "last_video": "20M50S_1734150050.mp4"}
```
其中2024121412为保存视频的文件，20M50S_1734150050.mp4为文件夹下的视频文件。这个文件代表这是上一次合并的最后一个视频。
通过修改这个文件，可以设置拼接起始点。


## 贡献

如果您喜欢此项目，请考虑给我们一个星标（star）！⭐⭐⭐
