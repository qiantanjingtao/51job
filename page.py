from urllib import request
from bs4 import BeautifulSoup
import re
from write_to_csv import Csv
import urllib.error
import socket


class Page(object):
    def __init__(self, page_num, job_count, write_num):
        self.page_num = page_num
        self.job_count = job_count
        self.write_num = write_num

    def count_page(self):
        self.page_num += 1

    def count_job(self):
        self.job_count += 1

    def count_writing(self):
        self.write_num += 1

    def one_page(self, url):
        html = request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        self.count_page()
        print('正在抓取第 ', self.page_num, '页：', url)

        dw_table = soup.find('div', id='resultList')
        el = dw_table.find_all('p', class_='t1')

        # 分析每一页上的50个工作
        for e in el:
            job_name = str(e.find('a').get_text()).strip()  # 获取一页当中的每一个job的名字
            job_url = e.find('a').get('href')
            if re.match('http://jobs.51job.com/', job_url) is None:  # 广告链接，跳过
                print('这不是一个应该采集的页面，将被跳过')
                continue
            self.count_job()
            print('正在分析第', self.job_count, '个工作：', job_name)
            # 为了不因为网络问题让程序奔溃，抓住错误后，就去分析下一个链接
            try:
                job_html = request.urlopen(job_url, timeout=10).read()
            except urllib.error.URLError:
                print('连接失败，正在重新连接...')
                continue
            except TimeoutError:
                print('连接失败，正在重新连接...')
                continue
            except socket.timeout:
                print('连接失败，正在重新连接...')
                continue

            job_soup = BeautifulSoup(job_html, 'html.parser')
            flag = 1  # 决定数据是否被存入csv文件中
            try:
                job_address = job_soup.find('div', class_='tHeader tHjob').find('span').get_text()  # 查找公司地点
                msg_type = job_soup.find('div', class_='tHeader tHjob').find('p',
                                                                             class_='msg ltype').get_text()  # 查找公司性质
                job_type = msg_type.strip().split('|')[0].strip()  # 由于刚刚查找的公司性质字符串有杂质，需要清理
                job_salary = job_soup.find('div', class_='tHeader tHjob').find('strong').get_text()  # 查找工资相关
                job_main = job_soup.find('div', class_='tCompanyPage').find('div', class_='tCompany_main').find_all(
                    'span')
                job_exp = job_main[0].get_text()
                job_university = job_main[1].get_text()
                job_re = job_soup.find('div', class_='bmsg job_msg inbox').get_text()
                job_k = job_soup.find('div', class_='bmsg job_msg inbox').find('div', class_='mt10').find('p',
                                                                                                          class_='fp').get_text()
            except AttributeError:
                flag = 0
                print('获取内容失败')  # 有重要内容无法获取，跳过对这份工作的分析
                continue
            else:
                # 上面的数据提取成功，继续提取字符串中的职业要求
                # 由于职业要求被包含在一段文字中，所以需要在文字中提取符合要求的数据
                temp = ''.join(job_re.split()).split('职能类别')[0]
                if temp.find('要求') >= 0:
                    if temp.find('要求：') >= 0:
                        job_req = temp.split('要求：')
                    else:
                        job_req = temp.split('要求')
                elif temp.find('标准') >= 0:
                    if temp.find('标准：') >= 0:
                        job_req = temp.split('标准：')
                    else:
                        job_req = temp.split('标准')
                elif temp.find('资格') >= 0:
                    if temp.find('资格：') >= 0:
                        job_req = temp.split('资格：')
                    else:
                        job_req = temp.split('资格')
                else:
                    job_req = [1, 2]  # 为了更好地进行处理，对不合格数据进行伪装
                for job_r in job_req:
                    if isinstance(job_r, str):
                        if job_r.startswith('1'):
                            job_requirement = job_r
                        elif job_r.startswith('：'):
                            job_requirement = job_r.strip('：')
                        elif job_r.startswith(':'):
                            job_requirement = job_r.strip(':')
                        else:
                            job_requirement = 0
                    else:
                        job_requirement = 0
                        break
                try:
                    job_kind = ' '.join(job_k.strip().split()).split('：')[1].strip(' ')
                except IndexError:
                    flag = 0   # 有重要内容无法获取，跳过对这份工作的分析
                    print('中文乱码，无法解析，跳过处理')
                    continue

            try:
                job_wel = job_soup.find('div', class_='tCompanyPage').find('div', class_='tCompany_main') \
                    .find('p', class_='t2').get_text()
                job_welfare = ' '.join(job_wel.split())
            except AttributeError:
                print('页面无福利显示,跳过')
                continue

            if job_university.find('招') >= 0:  # 没有写明学历要求，按‘无要求’处理
                job_university = '无要求'
            if flag == 0:
                print('无法分析职业要求，跳过')
            if flag == 0 or job_requirement == 0:  # 有重要数据缺失，不写入文件
                continue
            else:
                # 组装数据结构
                print(job_url, job_university, job_address)
                csv = Csv()
                csv.d['job_name'] = job_name
                csv.d['job_address'] = job_address
                csv.d['job_type'] = job_type
                csv.d['salary'] = job_salary
                csv.d['job_exp'] = job_exp
                csv.d['job_university'] = job_university
                csv.d['job_kind'] = job_kind
                csv.d['job_welfare'] = job_welfare
                csv.d['job_requirement'] = job_requirement

                csv.write_to_csv()
                self.count_writing()
                print('成功写入第', self.write_num, '条数据')

    # 在本页面查找下一页的地址，然后拿去查找数据，再查找新的一页地址，如此循环。
    @staticmethod
    def find_url(url):
        html = request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        url_finded = soup.find('div', class_='dw_page').find_all('li', class_='bk')[1].find('a').get('href')
        # 这里，由于bs4解析解析出来的网页链接不符合规范，需要重组链接
        url_list = url_finded.split('°')
        new_url = url_list[0] + '&deg' + url_list[1]
        return new_url


if __name__ == '__main__':
    start_url = 'http://search.51job.com/list/000000,000000,0000,00,9,99,%25E5%25A4%25A7%25E6%2595%25B0%25E6%258D' \
          '%25AE,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize' \
          '=99&providesalary=99&lonlat=0%2C0&' \
          'radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='

    page = Page(0, 0, 0)
    page.one_page(start_url)
    url = page.find_url(start_url)
    page.one_page(url)

    # 分析200页，每一页包含50条数据（包含其他链接）
    for i in range(200):
        url = page.find_url(url)
        page.one_page(url)
















