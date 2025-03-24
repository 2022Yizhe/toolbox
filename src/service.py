# 2. 服务层

import func.filter as filter
import func.file as file

is_processing = False  # 标记任务是否在进行中

class Service:

    def set_processing(self, value: bool):
        global is_processing
        is_processing = value

    def get_processing(self):
        return is_processing

    def get_result(self):
        return filter.result

    def start_filter(self, image_source: str, mode_separated: str, quality_filtered: str, cpu_workers: str):
        """ 过滤图片，按格式和质量分类，并删除重复文件 """
        cpu_workers = int(cpu_workers)
        conf = { 
            "image_source": image_source,
            'mode_separated': mode_separated,
            'quality_filtered': quality_filtered,
            'CPU_workers': cpu_workers
        }
        filter.filter_images(conf)
        global is_processing    # 标记任务结束
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