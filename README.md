# 51job
爬取51job网站上‘大数据’相关专业的数据


项目包含三个文件，第一个page.py是程序的入口文件，其中包含着Page类，能对每个具体职业的网页的数据进行分析。
具体的注释写在代码上。
write_to_csv.py文件是用于将Page文件分析好的数据写入csv文件中。

job.csv是爬取出来的数据，总共5340条，每一条包含9个属性。

注意：用的python版本是python 3.5
