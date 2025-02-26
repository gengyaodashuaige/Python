import time

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

BASE_URL = 'https://gf.cabr-fire.com/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
visited_urls = set()
data = []
id_counter = 1


def clean_url(url):
    """处理URL并标准化"""
    if 'm/' not in url:
        url = urljoin(BASE_URL, 'm/' + url)
    url = urljoin(BASE_URL, url).replace('/m/m', '/m/')
    return url.split('#')[0]


def get_content(url):
    """获取三级页面内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # content_div = soup.find('div', {'id': 'b_con', 'class': 'addsize15'})
        content_div = soup.find('div', {'id': 'b_con'})
        return content_div.get_text(separator='\n', strip=True) if content_div else ''
    except Exception as e:
        print(f"内容获取失败: {url} - {str(e)}")
        return ''


def process_level3(parent_id, level2_url):
    """处理三级标题"""
    global id_counter
    try:
        response = requests.get(level2_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        for ul in soup.select('ul.newsul'):
            li_tag = ul.find('li')
            a_tag = li_tag.find('a')
            if a_tag and a_tag['href']:
                level3_url = clean_url(a_tag['href'])
                if level3_url in visited_urls:
                    continue

                visited_urls.add(level3_url)
                content = get_content(level3_url)

                data.append({
                    'id': id_counter,
                    'parent_id': parent_id,
                    'level': 3,
                    'title': a_tag['title'],
                    'url': level3_url,
                    'content': content
                })
                id_counter += 1

                print('')
                print(f"正在获取三级标题 {a_tag['title']} 层数据")
    except Exception as e:
        print(f"三级处理失败: {level2_url} - {str(e)}")


def process_level2(parent_id, level1_url):
    """处理二级标题和分页"""
    global id_counter
    current_page = level1_url
    parent_ids = {}  # 保存每个二级标题的ID

    while current_page:
        try:
            response = requests.get(current_page, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 处理二级标题
            for a in soup.select('div.list-content a'):
                href = clean_url(a['href'])
                title = a.find(class_='text-img').text.strip()

                if href not in parent_ids:
                    parent_ids[href] = id_counter
                    data.append({
                        'id': id_counter,
                        'parent_id': parent_id,
                        'level': 2,
                        'title': title,
                        'url': href,
                        'content': ''
                    })
                    id_counter += 1

                    print('')
                    print(f"正在获取二级标题 {title} 层数据")

                    # 处理三级标题
                    process_level3(parent_ids[href], href)

            # 处理分页
            next_page = None
            pagination = soup.select('.pager a')
            for page in pagination:
                if '下一页' in page.text:
                    next_page = clean_url(page['href'])
                    break

            current_page = next_page if next_page and next_page not in visited_urls else None
            time.sleep(1)

        except Exception as e:
            print(f"二级处理失败: {current_page} - {str(e)}")
            break


def process_level1():
    """处理一级导航菜单"""
    global id_counter
    start_url = urljoin(BASE_URL, '/m/')

    try:
        response = requests.get(start_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        for dd in soup.select('dl.tag dd'):
            a_tag = dd.find('a')
            if a_tag and a_tag['href']:
                level1_url = clean_url(a_tag['href'])
                if level1_url in visited_urls:
                    continue

                visited_urls.add(level1_url)
                data.append({
                    'id': id_counter,
                    'parent_id': None,
                    'level': 1,
                    'title': a_tag.text.strip(),
                    'url': level1_url,
                    'content': ''
                })
                current_id = id_counter
                id_counter += 1

                print('')
                print(f"正在获取一级导航菜单 {a_tag.text.strip()} 层数据")

                # 处理下级内容
                process_level2(current_id, level1_url)
                time.sleep(1)

    except Exception as e:
        print(f"一级处理失败: {str(e)}")


def save_to_csv(filename):
    """保存为CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['序号', '父序号', '层级', '标题', '链接', '内容'])
        for item in data:
            writer.writerow([
                item['id'],
                item['parent_id'] or '',
                item['level'],
                item['title'],
                item['url'],
                item['content'][:50000]  # 限制内容长度防止溢出
            ])


if __name__ == "__main__":
    process_level1()
    save_to_csv('消防规范网.csv')
    print('-----------------------------------------------')
    print(f"共抓取 {len(data)} 条数据，已保存至 消防规范网.csv")