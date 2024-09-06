import json
import os
import subprocess


def main():
    while True:
        user_input = input("请输入命令 (1: m4s格式合并和转换； quit: 退出 ")  # 初始提示

        if user_input.lower() == "quit":
            print("退出程序...")
            break

        if user_input == "1":
            path = input("请输入bilibili文件夹路径: ")
            handle_search(path)


def handle_search(path):
    if os.path.exists(path):
        src_pair_list = []
        for dirpath, dirnames, filenames in os.walk(path):

            print(f"当前路径: {dirpath}")
            if dirnames:
                print(f"子目录: {dirnames}")
            if filenames:
                for filename in filenames:
                    name_without_extension, extension = os.path.splitext(filename)
                    full_path = os.path.join(dirpath, filename)
                    if extension == ".m4s":
                        handle_prefix_48(full_path)
                        match_and_merge(src_pair_list, full_path)
        print("合成完毕，请到 bilibili\output下查看合成文件。", '\n')
    else:
        print(f"路径 '{path}' 不存在。")


def match_and_merge(container, path, reminder=1):  # 第二个元素入列表时，列表大小符合要求，此时紧接合并操作
    if len(container) == reminder:
        src1 = path
        src2 = container.pop()
        dir_name = os.path.dirname(src1)
        output_file_name = handle_json(
            os.path.join(dir_name, 'videoInfo.json'))
        dir_name = os.path.dirname(dir_name)

        os.makedirs(os.path.join(dir_name, 'output'), exist_ok=True)

        output_file_name = os.path.join(dir_name, 'output', output_file_name + '.mp4')

        handle_ffmpeg(src1, src2, output_file_name)
        print("------------------------------------",'\n')
        container.clear()
    else:
        container.append(path)


def handle_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

            title = data.get("title", "")
            return f"{title}"

    except FileNotFoundError:
        print("无法找到 JSON 文件路径。")
    except json.JSONDecodeError:
        print("无法解码 JSON 文件。")


def handle_ffmpeg(file1, file2, output_path):
    try:
        # 构建 FFmpeg 命令
        command = [
            'ffmpeg', '-i',
            file1, '-i', file2, '-codec', 'copy', '-n',output_path
        ]
        # 执行命令
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 检查命令执行结果
        if process.returncode == 0:
            print(os.path.basename(output_path),"合成成功。")
        else:
            print("Error occurred:")
            print(stderr.decode())
    except Exception as e:
        print(f"An error occurred: {e}")


# 传入m4s 输出覆盖文件
def handle_prefix_48(file_path):
    if os.path.exists(file_path):
        temp_file = file_path + ".tmp"
        try:
            if handle_format(file_path):
                with open(file_path, 'rb') as infile:
                    infile.seek(9)
                    data = infile.read()
                with open(temp_file, 'wb') as outfile:  # 注意，写入临时文件
                    outfile.write(data)
                os.replace(temp_file, file_path)  # 用好的文件覆盖
        except IOError as e:
            print("IOError:", e)


def handle_format(file_path):
    with open(file_path, 'rb') as infile:
        header = infile.read(9)
    return header == b'000000000'


if __name__ == "__main__":
    main()
