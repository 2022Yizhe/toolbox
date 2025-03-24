# x. 图片分类（过滤），按模式分离，按质量分离，通过文件哈希查找删除重复图片

import os
from PIL import Image
import concurrent.futures
import time 

result = {
    "total_tasks": 0,
    "current_task": 0,
    "total_jobs": 0,
    "processed": 0,
    "progress": 0,
    "current_job": "没有正在进行的任务"
}

def clear_result():
    global result
    result['total_tasks'] = 0
    result['current_task'] = 0
    result['total_jobs'] = 0
    result['processed'] = 0
    result['progress'] = 0
    result['current_job'] = "没有正在进行的任务"


##
# To use this script, you need to offer the following configuration:
##
example_config = {
    'input_dir': "path\\to\\input_dir",
    'output_dir': "path\\to\\output_dir",
    'CPU_workers': 6
}

def process_format(filename, input_dir, output_dir):
    """处理单个图片格式的线程函数"""
    try:
        img_path = os.path.join(input_dir, filename)
        with Image.open(img_path) as img:
            # 强制加载图片数据以验证完整性
            img.load()
            
            # 获取文件信息
            file_size = os.path.getsize(img_path)
            print(f"[处理中] {filename}: {int(file_size/1024)}KB, 格式: {img.format}")

            # 根据格式创建输出目录
            output_subdir = img.format.upper() if img.format else "UNKNOWN"
            output_path = os.path.join(output_dir, output_subdir)
            os.makedirs(output_path, exist_ok=True)

            # 获取目标格式并检查是否支持透明通道
            if img.mode == 'RGBA':
                target_format = img.format.upper() if img.format else ''
                if target_format in ['JPEG', 'JPG', 'BMP']:  # 不支持Alpha的格式列表
                    img = img.convert('RGB')

            # 显式指定格式, 保存到对应目录
            img.save(
                os.path.join(output_path, filename),
                format=img.format,  # 确保按原始格式保存
                quality=100,        # 可选：设置 JPEG 质量参数
                **img.info          # 保留原始元数据
            )
            print(f"[完成] {filename} 已保存到 {output_subdir}/")
    except Exception as e:
        print(f"处理 {filename} 时出错: {str(e)}")


def separate_mode(input_dir: str, output_dir: str, CPU_workers: int = 1)-> dict:
    """多线程图片按格式分离主函数"""
    try:
        clear_result()  # 清空结果
        start_time = time.time()
        
        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)
        
        # 进度跟踪参数
        global result
        result["total_jobs"] = len(file_list)
        result['processed'] = 0

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务
            futures = [executor.submit(process_format, f, input_dir, output_dir) for f in file_list]
            
            # 显示进度
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"\n文件处理异常: {str(e)}")
                finally:    # 计算进度百分比
                    result['processed'] += 1
                    result['progress'] = result['processed'] / result['total_jobs'] * 100
                    result['current_job'] = file_list[result['processed'] - 1]
            
        end_time = time.time()
        return {'cost_time': end_time - start_time}
    except Exception as e:
        print(f"\n发生全局异常: {str(e)}")
        return {'error': str(e)}



# =========================================================================


def process_separate_quality(filename, input_dir, output_dir):
    """处理单个图片质量的线程函数"""
    try:
        img_path = os.path.join(input_dir, filename)
        with Image.open(img_path) as img:
            # 强制加载图片数据以验证完整性
            img.load()

            # 获取文件信息
            file_size = os.path.getsize(img_path)
            size_in_KB = int(file_size/1024)
            print(f"[处理中] {filename}: {size_in_KB}KB, 格式: {img.format}")

            # 根据质量创建输出目录
            output_subdir = "QUALITY" if size_in_KB >= 500 else "LOW"
            output_path = os.path.join(output_dir, output_subdir)
            os.makedirs(output_path, exist_ok=True)

            # 显式指定格式, 保存到对应目录
            img.save(
                os.path.join(output_path, filename),
                format=img.format,  # 确保按原始格式保存
                quality=100,         # 可选：设置 JPEG 质量参数
                **img.info          # 保留原始元数据 
            )
            print(f"[完成] {filename} 已保存到 {output_subdir}/")
    except Exception as e:
        print(f"处理 {filename} 时出错: {str(e)}")

def separate_quality(input_dir: str, output_dir: str, CPU_workers: int = 1)-> dict:
    """多线程图片按质量分离主函数"""
    try:
        clear_result()
        start_time = time.time()

        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务
            futures = [executor.submit(process_separate_quality, f, input_dir, output_dir) for f in file_list]
            
            # 显示进度（可选）
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"任务异常: {str(e)}")

        end_time = time.time()
        return {'cost_time': end_time - start_time}
    except Exception as e:
        print(e)


# ================================================================


def process_PNG_quality(filename, input_dir, output_dir):
    """处理单个图片 (PNG) 质量的线程函数"""
    try:
        img_path = os.path.join(input_dir, filename)
        with Image.open(img_path) as img:
            # 强制加载图片数据以验证完整性
            img.load()

            # 获取文件信息
            file_size = os.path.getsize(img_path)
            size_in_KB = int(file_size/1024)
            print(f"[处理中] {filename}: {size_in_KB}KB, 格式: {img.format}")

            # 根据质量创建输出目录
            output_subdir = "QUALITY" if size_in_KB >= 2000 else "LOW_QUALITY_LESS_2000KB"
            output_path = os.path.join(output_dir, output_subdir)
            os.makedirs(output_path, exist_ok=True)

            # 显式指定格式, 保存到对应目录
            img.save(
                os.path.join(output_path, filename),
                format=img.format,  # 确保按原始格式保存
                quality=100,         # 可选：设置 JPEG 质量参数
                **img.info          # 保留原始元数据 
            )
            print(f"[完成] {filename} 已保存到 {output_subdir}/")
    except Exception as e:
        print(f"处理 {filename} 时出错: {str(e)}")

def filter_PNG(input_dir: str, output_dir: str, CPU_workers: int = 1)-> dict:
    """多线程图片 (PNG) 按质量分离主函数"""
    try:
        clear_result()
        start_time = time.time()

        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务
            futures = [executor.submit(process_PNG_quality, f, input_dir, output_dir) for f in file_list]
            
            # 显示进度（可选）
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"任务异常: {str(e)}")

        end_time = time.time()
        return {'cost_time': end_time - start_time}
    except Exception as e:
        print(e)

# ================================================================


from hashlib import md5

def calculate_hash(file_path):
    """计算文件内容哈希值"""
    with open(file_path, "rb") as f:
        return md5(f.read()).hexdigest()
    

from threading import Lock

hash_lock = Lock()
known_hashes = set()  # 使用集合提升查询效率

def process_clear_duplicate(filename, input_dir):
    try:
        file_path = os.path.join(input_dir, filename)
        file_hash = calculate_hash(file_path)
        with hash_lock:
            if file_hash in known_hashes:
                os.remove(file_path)
                print(f"[删除重复] {filename}")
            else:
                known_hashes.add(file_hash)
    except Exception as e:
        print(f"处理 {filename} 失败: {str(e)}")


def clear_duplicate(input_dir: str, CPU_workers: int = 1)-> dict:
    """多线程图片查重主函数，使用文件哈希值校验"""
    try:
        clear_result()
        start_time = time.time()
        known_hashes.clear()

        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务
            futures = [executor.submit(process_clear_duplicate, f, input_dir) for f in file_list]
            
            # 显示进度（可选）
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"任务异常: {str(e)}")

        end_time = time.time()
        return {
            'cost_time': end_time - start_time,
            'removed_count': len(file_list) - len(known_hashes)
        }
    except Exception as e:
        print(e)


# ======================================================================================


def clear_cache(path: str)-> dict:
    """ 删除 cache 目录下的所有缓存文件夹和文件 (only JPEG and PNG) """
    start_time = time.time()
    total_jobs = 0 # 总文件数
    total_size = 0  # 总文件大小（B）

    # 遍历根目录
    for root, dirs, files in os.walk(path):
        # 遍历根目录下的文件
        for file in files:
            if file.endswith(".jpeg") or file.endswith(".jpg") or file.endswith(".png"):
                file_path = os.path.join(root, file)

                # 删除文件
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_jobs += 1
                    total_size += file_size
                    print(f"[清除缓存] Deleted file: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
    
    end_time = time.time()
    return {
        'cost_time': end_time - start_time,
        'removed_count': total_jobs,
        'total_size': total_size
    }
