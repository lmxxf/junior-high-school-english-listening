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

def generate_subtitles_recursively(root_directory):
    """
    为指定目录及其所有子目录下的 .mp3 文件生成 .vtt 字幕。
    """
    print(f"正在加载 Whisper 'base' 模型，初次加载需要下载，请稍候...")
    
    try:
        # 'base' 模型在速度和准确性之间取得了很好的平衡。
        model = whisper.load_model("base")
    except Exception as e:
        print(f"加载 Whisper 模型失败: {e}")
        print("请确保 PyTorch 已正确安装。可以尝试运行: pip install torch torchvision torchaudio")
        return

    print(f"模型加载完毕。开始递归处理目录: {root_directory}")

    if not os.path.isdir(root_directory):
        print(f"错误: 目录 '{root_directory}' 不存在。")
        return

    mp3_files_to_process = []
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith(".mp3"):
                mp3_files_to_process.append(os.path.join(dirpath, filename))

    if not mp3_files_to_process:
        print("在指定目录及其子目录中未找到 .mp3 文件。")
        return

    mp3_files_to_process.sort()
    total_files = len(mp3_files_to_process)
    print(f"找到了 {total_files} 个 .mp3 文件。")

    for index, mp3_path in enumerate(mp3_files_to_process):
        vtt_path = os.path.splitext(mp3_path)[0] + ".vtt"

        if os.path.exists(vtt_path):
            print(f"字幕已存在，跳过: {mp3_path}")
            continue

        print(f"[{index + 1}/{total_files}] 正在生成字幕: {mp3_path} ...")
        try:
            # 将语言明确设置为英语以获得最佳效果
            result = model.transcribe(mp3_path, language="en", verbose=False)

            # 使用 whisper 的工具函数来创建 VTT 字幕文件
            writer = whisper.utils.get_writer("vtt", os.path.dirname(vtt_path))
            writer(result, vtt_path, {})
            
            print(f"  -> 字幕已保存到: {vtt_path}")

        except Exception as e:
            print(f"  处理文件 {mp3_path} 时发生错误: {e}")

    print("\n所有文件处理完成。")

if __name__ == "__main__":
    # The script now processes the given directory and all its subdirectories.
    # The argument can be a specific directory like '初三上' or '.' for the current directory.
    if len(sys.argv) != 2:
        print("使用方法: python generate_subtitles.py <目标目录的路径>")
        print("例如，处理 '初三上' 文件夹及其子文件夹: python generate_subtitles.py 初三上")
        print("例如，处理当前文件夹及其子文件夹: python generate_subtitles.py .")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    generate_subtitles_recursively(target_directory)