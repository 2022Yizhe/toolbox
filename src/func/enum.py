result = {
    "current_task": "",
    "total_jobs": 0,
    "processed": 0,
    "current_job": "等待中"
}

def clear_result():
    result['current_task'] = ""
    result['total_jobs'] = 0
    result['processed'] = 0
    result['current_job'] = "等待中"

def set_current_task(task: str):
    result['current_task'] = task

def get_current_task():
    return result['current_task']

def set_total_jobs(total: int):
    result['total_jobs'] = total

def get_total_jobs():
    return result['total_jobs']

def set_processed(processed: int):
    result['processed'] = processed

def get_processed():
    return result['processed']

def set_current_job(job: str):
    result['current_job'] = job

def get_current_job():
    return result['current_job']

