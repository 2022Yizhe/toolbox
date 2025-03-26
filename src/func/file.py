# x. 文件工具，同构文件夹合并，文件提取，搜索目录并删除空的文件夹

import os   
import shutil

import func.enum as enum


def list_files(dir: str):
    """
    列出指定目录下的所有文件 (BFS 广度优先遍历)
    """
    try:
        for root, dirs, files in os.walk(dir):
            for file in files:
                print(file.split(os.sep)[-1])
    except Exception as e:
        raise e


def move_files(src: str, dst: str, target_dir: str|None):
    """
    移动目录或文件 (跨文件系统)
    """
    try:
        # 处理目标目录路径
        if target_dir is not None:
            dst = os.path.join(dst, target_dir)
        
        # 创建目标目录的父目录 (移动单个文件时确保目录存在)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        # 如果源是目录，移动其内容而非整个目录
        if os.path.isdir(src):
            # 确保目标目录存在
            os.makedirs(dst, exist_ok=True)
            # 遍历源目录中的项目
            for item in os.listdir(src):
                src_item = os.path.join(src, item)
                dst_item = os.path.join(dst, item)
                shutil.move(src_item, dst_item)
            # 可选：删除空的源目录
            if not os.listdir(src):
                os.rmdir(src)
        else:
            # 移动单个文件
            shutil.move(src, dst)
    except Exception as e:
        raise e


def copy_1file(src: str, dst: str):
    """
    复制单个文件 (跨文件系统)
    """
    try:
        # 创建目标文件的父级目录, 确保在移动单个文件时父级目录存在
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    except Exception as e:
        raise e


def copy_tree(src: str, dst: str, target_dir: str|None):
    """
    复制目录下的所有文件 (跨文件系统)
    """
    try:
        # 根据提示是否创建并复制到子级目录下
        if target_dir is not None:
            dst = os.path.join(dst, target_dir)
        shutil.copytree(src, dst, dirs_exist_ok=True)
    except Exception as e:
        raise e
    

##
# To use this script, you need to offer the following configuration:
##
example_config = {
    "src1": "C:\\Users\\Pictures\\2025-0312-0313",
    "src2": "C:\\Users\\Pictures\\2025-0314-0315",
    "dst": "path\\to\\merge"
}

def merge_dirs(src1: str, src2: str, dst: str):
    """
    合并两个目录结构完全相同的文件夹
    :param src1: 第一个源文件夹目录
    :param src2: 第二个源文件夹目录
    :param dst: 合并到的目标文件夹目录
    """
    # 统计文件数量
    file_count = int(0)
    for src in [src1, src2]:
        for root, dirs, files in os.walk(src):
            for f in files:
                if os.path.isfile(os.path.join(root, f)):
                    file_count += 1

    # 进度跟踪参数
    enum.clear_result()  # 清空结果

    enum.set_total_jobs(file_count)
    enum.set_processed(0)
    print(f"当前任务数量:{file_count}")
    
    try:
        # 统一处理所有源目录
        for src in [src1, src2]:
            for root, dirs, files in os.walk(src):
                # 计算相对路径
                rel_path = os.path.relpath(root, src)
                
                # 创建目标目录
                dst_dir = os.path.join(dst, rel_path)
                os.makedirs(dst_dir, exist_ok=True)

                for file in files:
                    # 创建单个目标文件路径
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_dir, file)

                    # 创建唯一文件名 dst_file
                    if os.path.exists(dst_file):
                        base, ext = os.path.splitext(file)
                        counter = 1
                        while True:
                            new_name = f"0A_{counter}_{file}{ext}"
                            new_path = os.path.join(dst_dir, new_name)
                            if not os.path.exists(new_path):    # 检查新的命名是否冲突
                                print(f"[merge] rename: {file} -> {new_name}")
                                dst_file = new_path
                                break
                            counter += 1
                    
                    # 复制文件（保留元数据）
                    copy_1file(src_file, dst_file)
                    print(f"[merge] copy {src_file}\n          -> {dst_file}")

                    # 记录进度
                    enum.set_processed(enum.get_processed() + 1)
                    enum.set_current_job(file)
    except Exception as e:
        print(f"[merge] error: {e}")
        raise e


##
# To use this script, you need to offer the following configuration:
##
example_config = {
    "src1": "C:\\Users\\Pictures\\2025-0312-0313",
    "dst": "path\\to\\extracted",
    "target_dir": "2025-0312-0313"
}

def extract_files(src: str, dst: str, target_dir: str|None):
    """
    提取目录下所有文件夹中的文件, 并移动到目录。根据 target_dir 是否为 None 来决定创建子级目录。
    :param src: 源文件夹目录
    :param dst: 目标文件夹目录
    :param target_dir: 创建的子级文件夹名称
    """
    try:
        for root, dirs, files in os.walk(src):
            for file in files:
                # 创建目标目录, 根据 target_dir 是否为 None 来决定创建子级目录
                if target_dir is not None:
                    dst_path = os.path.join(dst, target_dir)

                # 创建单个目标文件路径
                src_file = os.path.join(root, file)

                # 创建唯一文件名 dst_path
                if os.path.exists(os.path.join(dst_path, file)):
                    counter = 1
                    while True:
                        new_name = f"0A_{counter}_{file}"
                        new_path = os.path.join(dst_path, new_name)
                        if not os.path.exists(new_path):    # 检查新的命名是否冲突
                            print(f"[extract] rename: {file} -> {new_name}")
                            dst_path = new_path
                            break
                        counter += 1
                else:
                    dst_path = os.path.join(dst_path, file)

                # 复制文件（保留元数据）
                move_files(src_file, dst_path, None)
                print(f"[extract] move {src_file}\n             -> {dst_path}")
    except Exception as e:
        print(f"[extract] error: {e}")
        raise e
    

##
# To use this script, you need to offer the following configuration:
##
example_config = {
    "target": "path\\to\\.cache",
    "only_empty": True
}

def delete_dirs(target: str, only_empty = True):
    """
    删除空目录
    :param target: 目录路径
    :param only_empty: 是否只删除空目录
    """
    try:
        for root, dirs, files in os.walk(target, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if only_empty:
                    if len(os.listdir(dir_path)) == 0:
                        os.rmdir(dir_path)
                        print(f"[delete] empty: {dir_path}")
                else:
                    os.rmdir(dir_path)
                    print(f"[delete] all: {dir_path}")
    except Exception as e:
        print(f"[delete] error: {e}")
        raise e

