import os
from PIL import Image

SUPPORTED_IN = ["jpg", "jpeg", "png", "bmp", "webp", "tiff", "gif"]
SUPPORTED_OUT = ["jpg", "png", "bmp", "webp", "tiff"]


def _get_pil_save_format(suffix: str) -> str:
    """内部工具：把文件后缀映射为Pillow真正识别的save format字符串"""
    s = suffix.lower()
    if s == "jpg":
        return "JPEG"
    return s.upper()


def convert_image(input_path: str, output_format: str, output_dir: str = "./image_output") -> tuple[bool, str]:
    """
    单张图片格式转换（磁盘文件版本）
    :param input_path:输入图片路径
    :param output_format:输出格式 jpg/png/bmp/webp/tiff
    :param output_dir:输出文件夹
    :return: ok,message
    """
    output_format = output_format.lower()
    if output_format not in SUPPORTED_OUT:
        return False, f"不支持输出格式{output_format},支持:{SUPPORTED_OUT}"

    os.makedirs(output_dir, exist_ok=True)
    try:
        img = Image.open(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_file = os.path.join(output_dir, f"{base_name}.{output_format}")

        # jpg/jpeg不支持透明通道
        if output_format == "jpg" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(out_file)
        return True, f"转换完成：{out_file}"
    except Exception as e:
        return False, f"转换出错：{str(e)}"


def convert_image_bytes(image_bytes, output_format: str, filename: str):
    """
    内存字节流转换，用于streamlit上传文件，不写本地磁盘
    :raise ValueError: 格式不支持抛出异常
    """
    output_format = output_format.lower()
    if output_format not in SUPPORTED_OUT:
        raise ValueError(f"不支持输出格式{output_format}")

    from io import BytesIO
    img = Image.open(BytesIO(image_bytes))
    bio = BytesIO()

    # jpg 需要去掉透明
    if output_format == "jpg" and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # ✅修复bug：jpg → PIL识别的是 JPEG，不是 JPG
    pil_fmt = _get_pil_save_format(output_format)
    img.save(bio, format=pil_fmt)

    bio.seek(0)
    new_name = f"{os.path.splitext(filename)[0]}.{output_format}"
    return bio, new_name


if __name__ == "__main__":
    pass
