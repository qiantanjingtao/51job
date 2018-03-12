import csv


class Csv(object):
    def __init__(self):
        # 初始化数据结构
        self.d = {'job_name': 'j', 'job_address': 'j',
                  'job_type': 'j', 'job_salary': 'j',
                  'job_exp': 'j', 'job_university': 'j',
                  'job_kind': 'j', 'job_welfare': 'j',
                  'job_requirement': 'j'}

    def write_to_csv(self):
        with open('job.csv', 'a', newline='') as csv_file:  # newline为了防止写入时有空行现象
            writer = csv.writer(csv_file)
            try:
                writer.writerow([self.d['job_name'], self.d['job_address'],
                             self.d['job_type'], self.d['salary'],
                             self.d['job_exp'], self.d['job_university'],
                             self.d['job_kind'], self.d['job_welfare'],
                             self.d['job_requirement']])
            # 在对'job_requirement'内容写入时发现有可能会出现编码问题
            # 为了防止程序因此中断，加入try语句。
            except UnicodeEncodeError:
                return


