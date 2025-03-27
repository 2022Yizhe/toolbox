# x. 配置默认信息，使用当前环境参数

import os
import sys

def get_installation_path():
    if getattr(sys, 'frozen', False):
        # 如果程序是打包后的可执行文件
        installation_path = os.path.dirname(sys.executable)
    else:
        # 如果是未打包的Python脚本
        installation_path = os.path.dirname(os.path.abspath(__file__))
    
    return installation_path

def get_cpu_workers():
    return os.cpu_count()

root = get_installation_path()
cache = os.path.join(root, ".cache")

script1_conf = {    # 初始默认配置参数
    "image_source": None,
    'mode_separated': os.path.join(cache, "filter"),
    'quality_filtered': os.path.join(root, "filter"),
    'CPU_workers': 1
}

script2_conf = {    # 初始默认配置参数
    'src1': None,
    'src2': None,
    'dst': os.path.join(root, "merge")
}

script3_conf = {    # 初始默认配置参数
    'src': None,
    'dst': os.path.join(root, "extract"),
    'target_dir': None
}

script4_conf = {    # 初始默认配置参数
    'target': None,
    'only_empty': True
}