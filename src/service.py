# 2. 服务层

import func.filter as filter
import func.file as file
import func.enum as enum

import os
import time 

is_processing = False  # 标记任务是否在进行中

class Service:

    def set_processing(self):
        global is_processing
        is_processing = True

    def get_processing(self):
        return is_processing

    def get_result(self):
        return enum.result
    
    def stop_processing(self):
        # 标记任务结束
        time.sleep(0.2)         # 等待进度条更新 (避免最终进度条来不及更新)
        global is_processing
        is_processing = False

    def start_filter(self, image_source: str, cache: str, output: str, cpu_workers: str, conf: dict):
        """ 按格式和质量分类，查重，并删除重复文件 """
        cpu_workers = int(cpu_workers)

        by_mode = conf['by_mode']
        by_quality = conf['by_quality']
        cls_duplicate = conf['cls_duplicate']
        cls_cache = conf['cls_cache']

        # 规划任务流程
        last = False
        if by_mode:         # 按模式分类
            filter.separate_mode(image_source, cache, cpu_workers)
            last = True
        else:
            file.copy_tree(image_source, cache+"\\tmp", None)
            last = False
        if cls_duplicate:   # 查重
            for root, dirs, files in os.walk(cache):
                if dirs:
                    for dir in dirs:
                        filter.clear_duplicate(os.path.join(root, dir), cpu_workers)
        if by_quality:      # 按质量分类
            quality_boundary = int(conf['quality_boundary'])
            if last:
                filter.separate_quality(cache+"\\JPEG", output+"\\JPEG", cpu_workers, quality_boundary)
                filter.separate_quality(cache+"\\PNG", output+"\\PNG", cpu_workers, quality_boundary)
            else:
                filter.separate_quality(cache+"\\tmp", output, cpu_workers, quality_boundary)
        else:
            if last:
                file.move_files(cache+"\\JPEG", output+"\\JPEG", None)
                file.move_files(cache+"\\PNG", output+"\\PNG", None)
            else:
                file.move_files(cache+"\\tmp", output, None)
        if cls_cache:       # 删除缓存
            filter.clear_cache(cache+"\\JPEG")
            filter.clear_cache(cache+"\\PNG")
            filter.clear_cache(cache+"\\tmp")

            file.delete_dirs(cache, True)   # 同时删除空目录
        else:
            ...
        # 标记任务结束
        self.stop_processing()
    

    def start_merge(self, src1: str, src2: str, dst: str):
        """ 合并两个同构的文件夹 """
        file.merge_dirs(src1, src2, dst)

        # 标记任务结束
        self.stop_processing()


    def start_extract(self, src: str, dst: str, target_dir: str|None):
        """ 提取文件树中的所有文件，并移动到目标路径下 """
        file.extract_files(src, dst, target_dir)

        # 标记任务结束
        self.stop_processing()
    

    def start_delete(self, target: str, only_empty: str):
        """ 删除指定目录下的文件，当 only_empty 为 1 时，只删除空文件夹 """
        oe = True if only_empty == "1" else False
        file.delete_dirs(target, oe)

        # 标记任务结束
        self.stop_processing()