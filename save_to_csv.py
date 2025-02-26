# 保存数据到CSV

import csv


def save_nested_data_to_csv(data_list, filename):
    """
    将嵌套结构数据保存为CSV文件，包含自动序号和层级标记
    """
    # 准备数据存储
    rows = []
    global_counter = [1]  # 全局序号计数器

    def traverse(node, level, parent_seq=None):
        current_seq = global_counter[0]

        # 生成父序号（核心修复点）
        if parent_seq:
            # 仅当有父级时才构建层级路径
            hierarchy_path = f"{parent_seq}"
        else:
            hierarchy_path = ''

        # 提取当前节点的视频链接（如果有）
        video_url = ""
        if '内容' in node:
            # 只处理最深层级的视频链接（关键修复）
            for content in node['内容']:
                if isinstance(content, dict) and '内容' in content and isinstance(content['内容'], str):
                    video_url = content['内容']
                    break  # 只取第一个视频链接

        # 构建当前行数据
        rows.append({
            '序号': current_seq,
            '父序号': hierarchy_path,
            '层级': level,
            '标题': node['标题'],
            '链接': node['链接'],
            '视频链接': video_url
        })

        global_counter[0] += 1  # 递增计数器

        # 递归处理子节点（关键修改）
        if '内容' in node:
            for child in node['内容']:
                # 仅处理有标题的字典项（过滤视频链接项）
                if isinstance(child, dict) and '标题' in child:
                    traverse(child, level + 1, current_seq)

    # 遍历顶层数据
    for item in data_list:
        traverse(item, level=1)

    # 写入CSV文件
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['序号', '父序号', '层级', '标题', '链接', '视频链接'])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    # 示例数据
    # 这里放置你提供的原始数据
    input_data = [
        {
            '标题': "消防给水与消火栓系统",
            '链接': "https://v.1190119.com/m/xfgs/",
            '内容': [
                {
                    '标题': '室内消火栓',
                    '链接': 'https://v.1190119.com/m/snxhs/',
                    '内容': [
                        {
                            '标题': '室内消火栓-主要分类',
                            '链接': 'https://v.1190119.com/m/snxhs/339.html',
                            '内容': [{'内容': 'https://v.qq.com/txp/iframe/player.html?vid=v315407ko14'}]
                        }
                    ]
                },
                {'标题': '消防水泵及稳压泵控制',
                 '链接': 'https://v.1190119.com/m/xfsxt/',
                 '内容': [
                     {
                         '标题': '室内消火栓系统·消防水泵控制-报警联动控制',
                         '链接': 'https://v.1190119.com/m/xfsxt/193.html',
                         '内容': [{'内容': 'https://v.qq.com/txp/iframe/player.html?vid=d3320f4katl'}]
                     }
                 ]
                 }
            ]
        },
        {
            '标题': "消防系统-3D实景演示",
            '链接': "https://v.1190119.com/m/xfsystem/",
            '内容': [
                {
                    '标题': '防排烟系统基本概念（3D）',
                    '链接': 'https://v.1190119.com/m/fangpaiyanxitong/810.html',
                    '内容': [{'内容': 'https://v.qq.com/txp/iframe/player.html?vid=r3502jrfy2c'}]
                },
                {'标题': '开式细水雾灭火系统(3D）',
                 '链接': 'https://v.1190119.com/m/xsw/196.html',
                 '内容': [{'内容': 'https://v.qq.com/txp/iframe/player.html?vid=e096719hvkk'}]
                 }
            ]
        }
    ]
    # 执行完成后会自动生成 xxx.csv 文件
    save_nested_data_to_csv(input_data, 'xxx.csv')