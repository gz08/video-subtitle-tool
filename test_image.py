import os
from PIL import Image

# 获取本脚本所在文件夹（可移植基准路径）
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))


def check_image_file(file_path: str) -> dict:
    """
    检测单个图片文件：是否可以正常打开，获取真实格式、分辨率
    """
    result = {
        "path": file_path,
        "ok": False,
        "real_format": None,
        "width": None,
        "height": None,
        "error": None
    }
    try:
        with Image.open(file_path) as im:
            # 确认读取图片信息，强制加载像素，捕获损坏图片
            im.load()
            result["ok"] = True
            result["real_format"] = im.format
            result["width"] = im.width
            result["height"] = im.height
    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)
    return result


def scan_folder_images(folder: str):
    """扫描整个文件夹，检测所有文件，只尝试识别图片"""
    if not os.path.isdir(folder):
        print(f"文件夹不存在：{folder}")
        return

    ok_list = []
    bad_list = []

    for filename in os.listdir(folder):
        fullpath = os.path.join(folder, filename)
        if os.path.isdir(fullpath):
            continue
        res = check_image_file(fullpath)
        if res["ok"]:
            ok_list.append(res)
        else:
            bad_list.append(res)

    print("=" * 80)
    print(f"扫描目录：{folder}")
    print(f"✅正常图片数量: {len(ok_list)}")
    print(f"❌损坏/非图片数量: {len(bad_list)}")
    print("=" * 80)

    print("\n【✅正常图片列表】")
    for item in ok_list:
        print(f"{os.path.basename(item['path']):<45} | 格式:{item['real_format']:<6} | {item['width']}×{item['height']}")

    if len(bad_list) > 0:
        print("\n【❌损坏或者无法打开的文件】")
        for item in bad_list:
            print(f"{os.path.basename(item['path']):<45} | 错误：{item['error']}")


if __name__ == "__main__":
    # 相对路径：脚本同级目录下的 graph_transform
    target_folder = os.path.join(SCRIPT_ROOT, "graph_transform")
    scan_folder_images(target_folder)

