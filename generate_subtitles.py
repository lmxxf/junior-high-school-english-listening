
import os
import sys
import subprocess

# 检查 ffmpeg 是否已安装
try:
    subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
except (subprocess.CalledProcessError, FileNotFoundError):
    print("错误: ffmpeg 未安装或未在系统 PATH 中。")
    print("请先安装 ffmpeg。例如，在Debian/Ubuntu上运行: sudo apt update && sudo apt install ffmpeg")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("错误: whisper 库未安装。")
    print("请先运行: pip install openai-whisper")
    sys.exit(1)

def generate_subtitles_for_directory(directory):
    """
    为指定目录下的所有 .mp3 文件生成 .vtt 字幕。
    """
    print(f"正在加载 Whisper 'base' 模型，初次加载需要下载，请稍候...")
    
    try:
        # 'base' 模型在速度和准确性之间取得了很好的平衡。
        model = whisper.load_model("base")
    except Exception as e:
        print(f"加载 Whisper 模型失败: {e}")
        print("请确保 PyTorch 已正确安装。可以尝试运行: pip install torch torchvision torchaudio")
        return

    print(f"模型加载完毕。开始处理目录: {directory}")

    if not os.path.isdir(directory):
        print(f"错误: 目录 '{directory}' 不存在。")
        return

    mp3_files = sorted([f for f in os.listdir(directory) if f.endswith(".mp3")])

    if not mp3_files:
        print("在此目录中未找到 .mp3 文件。")
        return

    print(f"找到了 {len(mp3_files)} 个 .mp3 文件。")

    for filename in mp3_files:
        mp3_path = os.path.join(directory, filename)
        vtt_filename = os.path.splitext(filename)[0] + ".vtt"
        vtt_path = os.path.join(directory, vtt_filename)

        if os.path.exists(vtt_path):
            print(f"字幕已存在，跳过: {filename}")
            continue

        print(f"[{mp3_files.index(filename) + 1}/{len(mp3_files)}] 正在生成字幕: {filename} ...")
        try:
            # 将语言明确设置为英语以获得最佳效果
            result = model.transcribe(mp3_path, language="en", verbose=False)

            # 使用 whisper 的工具函数来创建 VTT 字幕文件
            writer = whisper.utils.get_writer("vtt", os.path.dirname(vtt_path))
            writer(result, vtt_path, {})
            
            print(f"  -> 字幕已保存到: {vtt_filename}")

        except Exception as e:
            print(f"  处理文件 {filename} 时发生错误: {e}")

    print("\n所有文件处理完成。")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python generate_subtitles.py <目标目录的路径>")
        print("例如: python generate_subtitles.py 初三上")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    generate_subtitles_for_directory(target_directory)
