# x. 图片分类（过滤），按模式分离，按质量分离，通过文件哈希查找删除重复图片

import os
from PIL import Image
import concurrent.futures
import time
import shutil

import func.enum as enum


##
# To use this script, you need to offer the following configuration:
##
example_config = {
    'input_dir': "path\\to\\input_dir",
    'output_dir': "path\\to\\output_dir",
    'CPU_workers': 6
}

# 提高像素限制（按需调整数值）
Image.MAX_IMAGE_PIXELS = 200000000

def process_format(imgPath: str, outDir: str, filename: str):
    """根据输入图像的透明通道进行格式转换 (JPEG/PNG)，并且尽可能保证图像的最大质量"""
    try:
        with Image.open(imgPath) as img:
            img.load()  # 延迟加载图像，确保每个线程都拥有完整的图像数据副本

            imgFormat = "1"
            imgSuffix = ".1"
            filename = os.path.splitext(filename)[0]   #  清除原图像可能不正确的后缀

            # 检查图像是否有透明通道，或者是否采用无损格式（PNG），然后进行格式转换
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                imgFormat = 'PNG'           # 转换为 PNG 格式
                imgSuffix = '.png'
            else:
                img = img.convert('RGB')    # 一律转换为 RGB 模式
                imgFormat = 'JPEG'          # 转换为 JPEG 格式
                imgSuffix = '.jpg'

            # 根据格式创建输出目录
            outDir = os.path.join(outDir, imgFormat)
            os.makedirs(outDir, exist_ok=True)

            # 添加文件名和后缀
            outPath = os.path.join(outDir, filename)
            outPath = f"{outPath}{imgSuffix}"

            # 准备保存参数
            save_args = {}
            if imgFormat == 'JPEG':
                # JPEG 优化参数
                save_args.update({
                    'quality': 95,                # 平衡质量与体积
                    'subsampling': 2,             # 启用子采样（4:2:0）
                    'progressive': True           # 启用渐进式编码
                })
                # 保留支持的元数据
                allowed_params = {'dpi', 'icc_profile'}
                save_args.update({k: v for k, v in img.info.items() if k in allowed_params})
            else:
                # PNG 优化参数
                save_args.update({
                    'compress_level': 9,       # 最高压缩级别
                    'optimize': True,          # 启用过滤优化
                    'bits': img.bits if hasattr(img, 'bits') else 8  # 保留色深
                })
                # 保留支持的元数据
                allowed_meta = {'dpi', 'icc_profile', 'compress_level'}
                save_args.update({k: v for k, v in img.info.items() if k in allowed_meta})
            img.save(outPath, format=imgFormat, **save_args)
            
            # print(f"[Format] Converted {imgPath} -> {outPath}")
    except Exception as e:
        print(f"[Format] Error Converting {filename}: {str(e)}")


def separate_mode(input_dir: str, output_dir: str, CPU_workers: int = 1)-> dict:
    """多线程图片按格式分离主函数"""
    try:
        start_time = time.time()
        print(f"\n[separate mode] 开始分离图片（按格式）: {input_dir}")
        
        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)
        
        # 进度跟踪参数
        enum.clear_result()  # 清空结果

        enum.set_current_task("separate mode")
        enum.set_total_jobs(len(file_list))
        enum.set_processed(0)

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务 (将列表推导式改为常规的循环)
            futures = []
            for f in file_list:
                imgPath = os.path.join(input_dir, f)
                future = executor.submit(process_format, imgPath, output_dir, f)
                futures.append(future)
            
            # 显示进度
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[separate mode] 处理异常: {str(e)}")
                finally:    # 记录进度
                    enum.set_processed(enum.get_processed() + 1)
                    enum.set_current_job(file_list[enum.get_processed() - 1])
            
        end_time = time.time()
        return {'cost_time': end_time - start_time}
    except Exception as e:
        print(f"\n[separate mode] 任务异常: {str(e)}")
        return {'error': str(e)}



# =========================================================================


def process_separate_quality(filename: str, input_dir:str, output_dir:str, quality_boundary:int):
    """处理单个图片质量的线程函数"""
    try:
        img_path = os.path.join(input_dir, filename)

        # 获取图像体积
        file_size = os.path.getsize(img_path)
        size_in_KB = int(file_size/1024)

        # 根据质量创建输出目录
        output_subdir = "QUALITY" if size_in_KB >= quality_boundary else "LOW"
        output_path = os.path.join(output_dir, output_subdir)
        os.makedirs(output_path, exist_ok=True)

        # 移动图像到对应目录
        shutil.move(img_path, os.path.join(output_path, filename))

        # print(f"[separate quality] 完成 {filename} 已移动到 {output_subdir}/")
    except Exception as e:
        print(f"[separate quality] 处理 {filename} 时出错: {str(e)}")


def separate_quality(input_dir: str, output_dir: str, CPU_workers: int = 1, quality_boundary: int = 500)-> dict:
    """多线程图片按质量分离主函数"""
    try:
        start_time = time.time()
        print(f"\n[separate mode] 开始分离图片（按质量）: {input_dir}")

        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)

        # 进度跟踪参数
        enum.clear_result()  # 清空结果

        enum.set_current_task("separate quality")
        enum.set_total_jobs(len(file_list))
        enum.set_processed(0)

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务 (将列表推导式改为常规的循环)
            futures = []
            for f in file_list:
                future = executor.submit(process_separate_quality, f, input_dir, output_dir, quality_boundary)
                futures.append(future)

            # 显示进度（可选）
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[separate quality] 处理异常: {str(e)}")
                finally:    # 记录进度
                    enum.set_processed(enum.get_processed() + 1)
                    enum.set_current_job(file_list[enum.get_processed() - 1])

        end_time = time.time()
        return {'cost_time': end_time - start_time}
    except Exception as e:
        print(f"\n[separate quality] 任务异常: {str(e)}")


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
    """处理单个图片查重的线程函数"""
    try:
        # 计算文件哈希值
        file_path = os.path.join(input_dir, filename)
        file_hash = calculate_hash(file_path)

        # 使用锁保护对共享资源的访问
        with hash_lock:
            # 检查哈希值是否已存在
            if file_hash in known_hashes:
                os.remove(file_path)
                print(f"[clear duplicate] {filename}")
            else:
                known_hashes.add(file_hash)
    except Exception as e:
        print(f"[clear duplicate] 处理 {filename} 失败: {str(e)}")


def clear_duplicate(input_dir: str, CPU_workers: int = 1)-> dict:
    """多线程图片查重主函数，使用文件哈希值校验"""
    try:
        start_time = time.time()
        print(f"\n[clear duplicate] 开始图像去重: {input_dir}")

        known_hashes.clear()

        # 获取所有文件，保存为列表
        file_list = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_list.append(f)
        
        # 进度跟踪参数

        enum.clear_result()  # 清空结果
        enum.set_current_task("clear duplicate")
        enum.set_total_jobs(len(file_list))
        enum.set_processed(0)

        # 创建线程池（根据 CPU 核心数自动调整）
        with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_workers) as executor:
            # 提交所有处理任务
            futures = [executor.submit(process_clear_duplicate, f, input_dir) for f in file_list]
            
            # 显示进度（可选）
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[clear duplicate] 处理异常: {str(e)}")
                finally:    # 记录进度
                    enum.set_processed(enum.get_processed() + 1)
                    enum.set_current_job(file_list[enum.get_processed() - 1])

        end_time = time.time()
        return {
            'cost_time': end_time - start_time,
            'removed_count': len(file_list) - len(known_hashes)
        }
    except Exception as e:
        print(f"\n[clear duplicate] 任务异常: {str(e)}")


# ======================================================================================


def clear_cache(path: str)-> dict:
    """ 删除 cache 目录下的所有缓存文件夹和文件 (only JPEG and PNG) """
    if not os.path.exists(path):
        print(f"\n[clear cache] 目录不存在: {path}")
        return None

    start_time = time.time()
    print(f"\n[clear cache] 开始清除缓存: {path}")

    total_jobs = 0  # 总文件数
    total_size = 0  # 总文件大小（B）

    # 进度跟踪参数
    enum.clear_result()  # 清空结果

    enum.set_current_task("clear cache")
    enum.set_total_jobs(len(os.listdir(path)))
    enum.set_processed(0)

    enum.set_current_job("remove cache files...")

    # 遍历根目录
    for root, dirs, files in os.walk(path):
        # 遍历根目录下的文件
        for file in files:
            try:
                if file.endswith(".jpg") or file.endswith(".png"):
                    # 删除文件
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)

                    total_jobs += 1
                    total_size += file_size
                    print(f"[clear cache] delete file: {file_path}")
            except Exception as e:
                print(f"\n任务异常: {file_path}: {e}")
            finally:    # 记录进度
                enum.set_processed(enum.get_processed() + 1)
    
    end_time = time.time()
    return {
        'cost_time': end_time - start_time,
        'removed_count': total_jobs,
        'total_size': total_size
    }
