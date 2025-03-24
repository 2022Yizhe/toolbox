# 2. 服务层

import func.filter as filter
import func.file as file

is_processing = False  # 标记任务是否在进行中

class Service:

    def set_processing(self):
        global is_processing
        is_processing = True

    def get_processing(self):
        return is_processing

    def get_result(self):
        return filter.result

    def start_filter(self, image_source: str, cache: str, output: str, cpu_workers: str, conf: dict):
        """ 过滤图片，按格式和质量分类，并删除重复文件 """
        cpu_workers = int(cpu_workers)

        by_mode = conf['by_mode']
        by_quality = conf['by_quality']
        cls_cache = conf['cls_cache']
        cls_duplicate = conf['cls_duplicate']

        # 规划任务流程
        last = False
        if by_mode:
            filter.separate_mode(image_source, cache, cpu_workers)
            last = True
        else:
            file.copy_tree(image_source, cache)
            last = False
        if by_quality:
            if last:
                filter.separate_quality(cache+"\\JPEG", output+"\\JPEG", cpu_workers)
                filter.separate_quality(cache+"\\PNG", output+"\\PNG", cpu_workers)
            else:
                filter.separate_quality(cache, output, cpu_workers)
        else:
            file.move_files(cache, output)
        
        if cls_duplicate:
            filter.clear_duplicate(output)
        else:
            ...
        if cls_cache:
            filter.clear_cache(cache)
        else:
            ...

        # 标记任务结束
        global is_processing 
        is_processing = False
    

    def start_merge(self, src1: str, src2: str, dst: str):
        """ 合并两个同构的文件夹 """
        file.merge_dirs(src1, src2, dst)


    def start_extract(self, src: str, dst: str, target_dir: str|None):
        """ 提取文件树中的所有文件，并移动到目标路径下 """
        file.extract_files(src, dst, target_dir)
    

    def start_delete(self, target: str, only_empty: str):
        """ 删除指定目录下的文件，当 only_empty 为 1 时，只删除空文件夹 """
        oe = True if only_empty == "1" else False
        file.delete_dirs(target, oe)