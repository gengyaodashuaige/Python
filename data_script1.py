# -*- coding: utf-8 -*-
# 安装依赖：pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup
import csv
import chardet

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Referer': 'https://v.1190119.com/'
}


def extract_tag_data(html_content, file_name):
    """提取dl.tag中的结构化数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    tag_dl = soup.find('dl', class_='tag')

    if not tag_dl:
        print("未找到tag列表")
        return []

    data_list = []
    # 遍历所有dd标签
    for dd in tag_dl.find_all('dd'):
        # 提取a标签内容
        a_tag = dd.find('a')
        if a_tag and a_tag.has_attr('href'):
            # 处理属性名称拼写容错（tit1e->title）
            title = a_tag.get('title') or a_tag.get('tit1e', '') or a_tag.text.strip()
            # 处理链接完整与不完整容错
            from supplement_url import montage_url
            href = montage_url(file_name, a_tag['href'].strip())
            print("")
            print(f"正在获取{title}层数据：")
            data = get_next_data(title, href, file_name)
            print("")
            print(f"{title}层共成功提取 {len(data)} 条标签")
            print("-------------------------------------------------")
            item = {
                '标题': title,
                '链接': href,
                '内容': data
            }
            data_list.append(item)

    return data_list


def get_next_data(title, url, file_name):
    data_list = []
    bottom = True
    while bottom:
        # 获取第下一层级信息
        try:
            # 消防大讲堂特例
            # if url=='/mhttp://v.1190119.com/thg/1082.html':
            #     url = 'http://v.1190119.com/m/thg/1082.html'
            response_son = requests.get(url, headers=headers, timeout=10)
            response_son.encoding = 'utf-8'  # 强制使用UTF-8编码

            # 自动检测网页真实编码（需安装chardet库：pip install chardet）
            detected_encoding = chardet.detect(response_son.content)['encoding']
            response_son.encoding = detected_encoding  # 替换自动检测的编码
            # son_tag_data = extract_tag_data_son(response.text, title, url, file_name)

            if response_son.status_code == 200:

                """提取标签中的结构化数据"""
                soup = BeautifulSoup(response_son.text, 'html.parser')

                video_div = soup.find('div', class_='subpages') # 消防大讲堂
                # video_div = soup.find('div', class_='subpages') # 消防资源网
                if not video_div: # 是否最后一层

                    no_data_list_div = soup.find('div', class_='no_data-list')
                    # 遍历所有p标签
                    for li in no_data_list_div.find_all('div', class_='w100 title-list'):
                        p = li.find('div', class_='title-list-content fr').find('p')
                        # 提取a标签内容
                        a_tag = p.find('a')
                        if a_tag and a_tag.has_attr('href'):
                            # 处理属性名称拼写容错（tit1e->title）
                            son_title = a_tag.get('title') or a_tag.get('tit1e', '') or a_tag.text.strip()
                            # 处理链接完整与不完整容错
                            from supplement_url import montage_url
                            son_href = montage_url(file_name, a_tag['href'].strip())
                            next_data = get_next_data(son_title, son_href, file_name)
                            item = {
                                '标题': son_title,
                                '链接': son_href,
                                '内容': next_data
                            }
                            data_list.append(item)
                    print("")
                    print(f"正在获取下层数据...")
                    print(f"...共成功提取 {len(data_list)} 条标签")
                    break
                else:
                    iframe = video_div.find('iframe')
                    # 提取iframe标签内容
                    if iframe and iframe.has_attr('data-src'):
                        item = {
                            '内容': iframe.get('data-src')
                        }
                        data_list.append(item)
                    break
            else:
                print(f"子标题层请求失败，状态码：{response_son.status_code}")
                break

        except Exception as e:
            print(f"子标题层发生错误：{str(e)}")
            break

    return data_list


def main(url, file_name):

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'  # 强制使用UTF-8编码

        # 自动检测网页真实编码（需安装chardet库：pip install chardet）
        detected_encoding = chardet.detect(response.content)['encoding']
        response.encoding = detected_encoding  # 替换自动检测的编码

        if response.status_code == 200:
            tag_data = extract_tag_data(response.text, file_name)

            if tag_data:
                print(f"共成功提取 {len(tag_data)} 条标签数据")
                # 保存数据到CSV
                from save_to_csv import save_nested_data_to_csv
                save_nested_data_to_csv(tag_data, file_name)
            else:
                print("标题层未提取到有效数据")
        else:
            print(f"标题层请求失败，状态码：{response.status_code}")

    except Exception as e:
        print(f"标题层发生错误：{str(e)}")


if __name__ == "__main__":
    main('xxx.csv')
    # 执行完成后会自动生成 xxx.csv 文件