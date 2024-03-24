import xml.etree.ElementTree as ET
from datetime import datetime


def stamp2time(timestamp):
    # 将字符串转换为datetime对象
    dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    # 将datetime对象格式化为指定的字符串格式
    formatted_dt = dt.strftime('%a, %d %b %Y %H:%M:%S +0900')
    return formatted_dt


def yna2rss(xml):
    root = root = ET.fromstring(xml)
    # 遍历XML文件中的元素
    for child in root:
        # print(child.tag, child.attrib)
        for subchild in child:
            # print(subchild.tag, subchild.text)
            if subchild.tag == 'item':
                for subsubchild in subchild:
                    # print(subsubchild.tag, subsubchild.text)
                    if subsubchild.tag == 'id':
                        subsubchild.tag = 'guid'
                    elif subsubchild.tag == 'pubDate':
                        subsubchild.text = stamp2time(subsubchild.text)
    # 将ElementTree导出成字符串
    xml_str = ET.tostring(root, encoding='utf8', method='xml').decode('utf8')
    return xml_str


if __name__ == '__main__':
    with open('news.xml', encoding='utf8') as f:
        tmp = yna2rss(f.read())
