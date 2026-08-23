import os

# 改成你本地代码文件夹的完整路径
root_dir = r"C:\Users\19879\Desktop\new"

def read_all_py_code(folder):
    all_content = ""
    for path, dirs, files in os.walk(folder):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(path, fname)
                all_content += f"===== 文件名：{fname} =====\n"
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        all_content += f.read() + "\n\n"
                except:
                    with open(fpath, "r", encoding="gbk") as f:
                        all_content += f.read() + "\n\n"
    return all_content

if __name__ == "__main__":
    res = read_all_py_code(root_dir)
    # 打印全部代码，你全选复制就行
    print(res)
    # 同时保存到本地txt，方便复制
    with open("全部代码汇总(新).txt", "w", encoding="utf-8") as f:
        f.write(res)