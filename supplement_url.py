# 三个网站的链接 拼接方式不同

def montage_url(name, href):
    if name == '消防大讲堂.csv':
        if href.find('//v.1190119.com/') == -1:
            return 'https://v.1190119.com' + href
        return href
    elif name == '消防资源网.csv':
        if href.find('//b.1190119.com/') == -1:
            return 'https://b.1190119.com/m/' + href
        return href
    elif name == '消防规范网':
        if href.find('//gf.cabr-fire.com/') == -1:
            return 'https://gf.cabr-fire.com/m/' + href
        return href
    else:
        return href
