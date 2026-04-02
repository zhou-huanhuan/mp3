# B站视频转MP3下载工具

这是一个可以将Bilibili（B站）视频转换为MP3音频文件并下载歌词字幕的命令行工具。

## 功能特点

- 🎵 将B站视频转换为高质量的MP3音频（192Kbps）
- 📝 自动下载和转换歌词字幕为LRC格式
- 🔄 支持BV号和av号两种视频ID格式
- 📀 嵌入元数据到MP3文件中
- 🌐 支持短链接 (b23.tv) 和完整链接

## 依赖要求

- Python 3.8+
- yt-dlp
- ffmpeg（用于音频转换）
- requests
- beautifulsoup4

## 安装

```bash
# 安装Python依赖
pip install yt-dlp requests beautifulsoup4

# 确保已安装ffmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows: 从 https://ffmpeg.org/download.html 下载
```

## 使用方法

### 基本用法

```bash
python bilibili_to_mp3.py <B站视频链接>
```

### 示例

```bash
# 下载单个视频
python bilibili_to_mp3.py https://www.bilibili.com/video/BV1xxxxxx

# 指定输出目录
python bilibili_to_mp3.py https://www.bilibili.com/video/BV1xxxxxx -o ./downloads

# 使用短链接
python bilibili_to_mp3.py https://b23.tv/xxxxxx
```

## 输出文件

程序会生成两个文件：
- `视频标题.mp3` - 音频文件
- `视频标题.lrc` - 歌词字幕文件（如果可用）

## 注意事项

1. **版权问题**：请确保您有权利下载和使用相关音频内容，仅用于个人学习研究。

2. **会员视频**：部分需要大会员权限的视频可能无法下载，或者需要配置cookie。

3. **歌词可用性**：并非所有视频都有字幕/歌词，如果没有可用字幕，将只下载音频文件。

4. **网络问题**：由于网络原因，下载可能需要较长时间，请耐心等待。

## 故障排除

### 下载失败的可能原因：
- 视频链接无效或视频已被删除
- 视频需要大会员权限
- 网络连接问题
- 需要登录（可以尝试在浏览器中登录后导出cookie）

### 提高成功率的方法：

如果需要下载会员视频或遇到限制，可以配置yt-dlp使用浏览器cookie：

```bash
# 使用Chrome/Edge的cookie
yt-dlp --cookies-from-browser chrome [其他选项] <URL>
```

## 技术实现

本工具使用以下技术：
- **yt-dlp**: 强大的视频下载库，支持B站
- **ffmpeg**: 音频格式转换
- **requests + BeautifulSoup**: 网页解析和API调用
- **自定义歌词提取**: 从B站API获取字幕并转换为LRC格式

## 许可证

本工具仅供学习研究使用，请勿用于商业目的。
