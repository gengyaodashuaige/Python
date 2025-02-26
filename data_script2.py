import requests
from bs4 import BeautifulSoup
import csv
import time
import chardet

BASE_URL = 'https://b.1190119.com/m/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Referer': 'https://v.1190119.com/'
}

def clean_title(title):
    """清洗标题，去除序号和首尾空格"""
    return title.split('、', 1)[-1].strip()


def get_page_content(url):
    """获取页面内容（文字、图片、链接）"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = []

        # 提取所有文字内容
        for element in soup.find_all(['p', 'section']):
            text = element.get_text(separator=' ', strip=True)
            if text:
                content.append(text)

        # 提取图片链接
        for img in soup.find_all('img', src=True):
            content.append(f"[图片] {img['src']}")

        # 提取内链
        for a in soup.find_all('a', href=True):
            if a['href'].startswith(('http', '//')):
                content.append(f"[链接] {a['href']}")
            else:
                content.append(f"[内链] {BASE_URL}{a['href']}")

        return '\n'.join(content)

    except Exception as e:
        print(f"获取内容失败: {url} - {str(e)}")
        return ''


def parse_main_page(html):
    """解析主页面结构"""
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # 处理每个表格
    for table in soup.find_all('table'):
        # 提取一级标题
        caption = table.find('caption')
        if caption and caption.strong:
            level1 = {
                'id': len(data) + 1,
                'parent_id': None,
                'level': 1,
                'title': clean_title(caption.strong.text),
                'link': BASE_URL + caption['onclick'].split("'")[1],
                'content': ''
            }
            data.append(level1)
            print("")
            print(f"正在获取{clean_title(caption.strong.text)}层数据")



            # 处理二级标题
            for tr in table.find_all('tr'):
                a_tag = tr.find('a')
                if a_tag and a_tag.strong:
                    level2 = {
                        'id': len(data) + 1,
                        'parent_id': level1['id'],
                        'level': 2,
                        'title': clean_title(a_tag.strong.text),
                        'link': BASE_URL + a_tag['href'],
                        'content': get_page_content(BASE_URL + a_tag['href'])
                    }
                    data.append(level2)
                    time.sleep(1)  # 请求间隔

            print("")
            print(f"{clean_title(caption.strong.text)}层共成功提取 {len(table.find_all('tr'))} 条标签")
            print("-------------------------------------------------")
    return data


def save_to_csv(data, filename):
    """保存数据到CSV"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['序号', '父序号', '层级', '标题', '链接', '内容'])
        for item in data:
            writer.writerow([
                item['id'],
                item['parent_id'] or '',
                item['level'],
                item['title'],
                item['link'],
                item['content'][:5000]  # 限制内容长度防止单元格溢出
            ])


def main(url, file_name):

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'  # 强制使用UTF-8编码

        # 自动检测网页真实编码（需安装chardet库：pip install chardet）
        detected_encoding = chardet.detect(response.content)['encoding']
        response.encoding = detected_encoding  # 替换自动检测的编码

        if response.status_code == 200:
            tag_data = parse_main_page(response.text)

            if tag_data:
                print(f"共成功提取 {len(tag_data)} 条标签数据")
                # 保存数据到CSV
                save_to_csv(tag_data, file_name)
            else:
                print("标题层未提取到有效数据")
        else:
            print(f"标题层请求失败，状态码：{response.status_code}")

    except Exception as e:
        print(f"标题层发生错误：{str(e)}")


# 使用示例
if __name__ == "__main__":
    # 假设这是主页面HTML内容
    main_page_html = """
    [这里粘贴您提供的第一个HTML内容]
    """

    # 解析主页面
    structured_data = parse_main_page(main_page_html)

    # 保存结果
    save_to_csv(structured_data, 'structured_content.csv')
    print("数据已保存至 structured_content.csv")