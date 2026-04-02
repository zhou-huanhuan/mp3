#!/usr/bin/env python3
"""
B站视频转MP3下载工具（带歌词字幕）

用法:
    python bilibili_to_mp3.py <B站视频链接>

示例:
    python bilibili_to_mp3.py https://www.bilibili.com/video/BV1xxxxxx
"""

import os
import re
import sys
import json
import subprocess
import argparse
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖：pip install requests beautifulsoup4")
    sys.exit(1)


def get_video_id(url: str) -> str:
    """从B站链接中提取视频ID (BV号或av号)"""
    # 匹配 BV 号
    bv_match = re.search(r'(BV[a-zA-Z0-9]+)', url)
    if bv_match:
        return bv_match.group(1)
    
    # 匹配 av 号
    av_match = re.search(r'av(\d+)', url)
    if av_match:
        return f"av{av_match.group(1)}"
    
    raise ValueError(f"无法从链接中提取视频ID: {url}")


def get_video_info(video_id: str) -> dict:
    """获取视频基本信息（标题等）"""
    # 确定是BV号还是av号
    if video_id.startswith("BV"):
        url = f"https://www.bilibili.com/video/{video_id}"
    else:
        url = f"https://www.bilibili.com/video/{video_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 尝试从页面中提取标题
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('meta', {'name': 'title'})
        if title_tag and title_tag.get('content'):
            title = title_tag['content']
            # 清理标题中的非法字符
            title = re.sub(r'[\\/:*?"<>|]', '_', title)
            return {'title': title.strip()}
    except Exception as e:
        print(f"警告：获取视频信息失败: {e}")
    
    return {'title': video_id}


def download_audio_and_lyrics(video_url: str, output_dir: str = ".") -> str:
    """
    下载B站视频音频并提取/下载歌词
    
    参数:
        video_url: B站视频链接
        output_dir: 输出目录
    
    返回:
        生成的MP3文件路径
    """
    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"正在处理视频: {video_url}")
    
    # 提取视频ID
    video_id = get_video_id(video_url)
    print(f"视频ID: {video_id}")
    
    # 获取视频信息
    video_info = get_video_info(video_id)
    base_title = video_info.get('title', video_id)
    print(f"视频标题: {base_title}")
    
    # 使用 yt-dlp 下载音频并尝试获取字幕
    temp_output = str(output_dir / f"{video_id}")
    
    # yt-dlp 命令：下载最佳音频，转换为MP3，并下载字幕
    cmd = [
        'yt-dlp',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--audio-quality', '192K',
        '--write-sub',           # 下载字幕
        '--write-auto-sub',      # 下载自动生成的字幕
        '--sub-langs', 'zh-Hans,zh-CN,zh,en',  # 优先中文简体字幕
        '--sub-format', 'lrc',   # 尝试下载LRC格式（如果可用）
        '--convert-subs', 'lrc', # 将字幕转换为LRC格式
        '--embed-metadata',      # 嵌入元数据
        '-o', temp_output,
        '--no-playlist',         # 只下载单个视频，不下载整个列表
        '--no-warnings',
        video_url
    ]
    
    print("正在下载音频和字幕...")
    print("(这可能需要几分钟，取决于视频长度和网络速度)")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode != 0:
            print(f"yt-dlp 输出:\n{result.stdout}")
            print(f"yt-dlp 错误:\n{result.stderr}")
            
            # 如果带字幕下载失败，尝试不带字幕下载
            print("\n尝试不带字幕重新下载音频...")
            cmd_no_sub = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '192K',
                '--embed-metadata',
                '-o', temp_output,
                '--no-playlist',
                '--no-warnings',
                video_url
            ]
            result = subprocess.run(cmd_no_sub, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                raise RuntimeError(f"下载失败: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("下载超时，请检查网络连接或视频是否可访问")
    
    # 查找生成的文件
    mp3_file = None
    lrc_file = None
    
    for file in output_dir.glob(f"{video_id}.*"):
        if file.suffix == '.mp3':
            mp3_file = file
        elif file.suffix == '.lrc':
            lrc_file = file
    
    # 重命名文件为更具可读性的名称
    if mp3_file:
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', base_title)
        new_mp3_name = output_dir / f"{safe_title}.mp3"
        new_lrc_name = output_dir / f"{safe_title}.lrc"
        
        if mp3_file != new_mp3_name:
            mp3_file.rename(new_mp3_name)
            mp3_file = new_mp3_name
        
        if lrc_file:
            if lrc_file != new_lrc_name:
                lrc_file.rename(new_lrc_name)
                lrc_file = new_lrc_name
    
    # 如果没有找到LRC文件，尝试从B站API获取歌词
    if not lrc_file and video_id.startswith("BV"):
        print("\n尝试从B站API获取歌词...")
        try:
            lrc_content = fetch_bilibili_lyrics(video_id)
            if lrc_content:
                lrc_file = output_dir / f"{safe_title}.lrc"
                with open(lrc_file, 'w', encoding='utf-8') as f:
                    f.write(lrc_content)
                print(f"✓ 歌词已保存: {lrc_file}")
        except Exception as e:
            print(f"获取歌词失败: {e}")
    
    # 验证结果
    if not mp3_file or not mp3_file.exists():
        raise RuntimeError("未能生成MP3文件")
    
    print(f"\n{'='*50}")
    print(f"✓ 下载完成!")
    print(f"音频文件: {mp3_file.absolute()}")
    if lrc_file and lrc_file.exists():
        print(f"歌词文件: {lrc_file.absolute()}")
    else:
        print("⚠ 未找到歌词文件（该视频可能没有可用字幕）")
    print(f"{'='*50}")
    
    return str(mp3_file)


def fetch_bilibili_lyrics(video_id: str) -> str:
    """
    尝试从B站API获取歌词
    
    注意：这个方法可能需要有效的cookie才能访问某些接口
    """
    # 这里尝试使用一些公开的接口
    # 由于B站API的复杂性，这可能不总是有效
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://www.bilibili.com/video/{video_id}',
    }
    
    # 方法1: 尝试通过视频页面获取字幕信息
    try:
        url = f'https://www.bilibili.com/video/{video_id}'
        response = requests.get(url, headers=headers, timeout=10)
        
        # 查找subtitle信息
        match = re.search(r'"subtitles":\s*(\[.*?\])', response.text)
        if match:
            subtitles = json.loads(match.group(1))
            if subtitles:
                # 获取第一个字幕的URL
                subtitle_url = subtitles[0].get('subtitle_url')
                if subtitle_url:
                    # 字幕URL通常是相对路径
                    if subtitle_url.startswith('//'):
                        subtitle_url = 'https:' + subtitle_url
                    elif subtitle_url.startswith('/'):
                        subtitle_url = 'https://www.bilibili.com' + subtitle_url
                    
                    sub_response = requests.get(subtitle_url, headers=headers, timeout=10)
                    sub_data = sub_response.json()
                    
                    # 转换为LRC格式
                    if 'body' in sub_data:
                        return convert_subtitle_to_lrc(sub_data['body'])
    except Exception as e:
        print(f"获取字幕信息失败: {e}")
    
    return ""


def convert_subtitle_to_lrc(subtitle_body: list) -> str:
    """将B站字幕JSON转换为LRC格式"""
    lrc_lines = []
    
    for item in subtitle_body:
        if 'from' in item and 'content' in item:
            from_time = item['from']
            content = item['content']
            
            # 转换时间为MM:SS.ms格式
            minutes = int(from_time // 60)
            seconds = from_time % 60
            time_str = f"[{minutes:02d}:{seconds:06.3f}]"
            
            lrc_lines.append(f"{time_str}{content}")
    
    return "\n".join(lrc_lines)


def main():
    parser = argparse.ArgumentParser(
        description='B站视频转MP3下载工具（带歌词字幕）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s https://www.bilibili.com/video/BV1xxxxxx
  %(prog)s https://b23.tv/xxxxxx -o ./downloads
        """
    )
    parser.add_argument('url', help='B站视频链接')
    parser.add_argument('-o', '--output', default='.', 
                       help='输出目录 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    # 验证链接
    if 'bilibili.com' not in args.url and 'b23.tv' not in args.url:
        print("错误: 请提供有效的B站视频链接")
        print("示例: https://www.bilibili.com/video/BV1xxxxxx")
        sys.exit(1)
    
    try:
        output_file = download_audio_and_lyrics(args.url, args.output)
        print(f"\n成功! 文件保存在: {output_file}")
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n可能的原因:")
        print("  1. 视频链接无效或视频已被删除")
        print("  2. 视频需要大会员权限")
        print("  3. 网络连接问题")
        print("  4. 需要登录（可以尝试在浏览器中登录后导出cookie）")
        sys.exit(1)


if __name__ == '__main__':
    main()
