"""
函数1：get_project_root()只是为了获取我所有文件的根目录 比如E:rag 没有别的用
函数2：get_abs_path()是为了后面解读代码的时候 能精确到具体的文件 通过根目录找到具体的文件位置读取
"""



import os
def get_project_root() -> str:
    """
    获取工程所在的根目录 return根目录字符串
    """

    current_file = os.path.abspath(__file__) # 获取当前文件的绝对路径
    current_dir = os.path.dirname(current_file) # 获取当前文件夹的绝对路径
    project_root = os.path.dirname(current_dir) # 获取工程的根目录
    # 注意：这里定死了只返回两层就到根目录 要修改的话再加一级os.path.dirname

    return project_root

# abs:absolute
def get_abs_path(relativate_path: str) -> str:
    """
    传递相对路径(相对于根目录的相对路径)，得到绝对路径
    relative_path: 相对路径
    return: 绝对路径
    """

    # 调用上面的函数 获取当前根目录的绝对路径
    project_root = get_project_root()
    return os.path.join(project_root,relativate_path)