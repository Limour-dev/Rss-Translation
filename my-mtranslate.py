import configparser
import datetime
import hashlib
import os
import time
from urllib import parse
from nrss.yna_cn2rss import yna2rss

import requests


def get_md5_value(src):
    _m = hashlib.sha256()
    _m.update(src.encode(encoding="utf-8"))
    return _m.hexdigest()


def getTime(e):
    try:
        struct_time = e.published_parsed
    except AttributeError:
        struct_time = time.localtime()
    return datetime.datetime(*struct_time[:6])


def update_readme(links):
    with open("README.md", "r+", encoding="UTF-8") as f:
        list1 = f.readlines()
    
    list1 = list1[:13] + [x.replace(r'](rss', r'](../../raw/main/rss') for x in links]
    with open("README.md", "w+", encoding="UTF-8") as f:
        f.writelines(list1)


def tran(sec, max_item):
    # 获取各种配置信息
    xml_file = os.path.join(BASE, f'{get_cfg(sec, "name")}.xml')
    url = get_cfg(sec, "url")
    old_md5 = get_cfg(sec, "md5")
    # 读取旧的 MD5 散列值
    source, target = get_cfg_tra(sec, config)
    global links
    links += [
        " - %s [%s](%s) -> [%s](%s)\n"
        % (sec, url, (url), get_cfg(sec, "name"), parse.quote(xml_file))
    ]
    # 判断 RSS 内容是否有更新
    try:
        r = requests.get(url, timeout=5)
        new_md5 = get_md5_value(r.text)
    except Exception as e:
        print("Error occurred when fetching RSS content for %s: %s" % (sec, str(e)))
        return
    if old_md5 == new_md5:
        print("No update needed for %s" % sec)
        return
    else:
        print("Updating %s..." % sec)
        set_cfg(sec, "md5", new_md5)

    rss = yna2rss(r.text)
    
    try:
        os.makedirs(BASE, exist_ok=True)
    except Exception as e:
        print("Error occurred when creating directory %s: %s" % (BASE, str(e)))
        return

    # 如果 RSS 文件存在，则删除原有内容
    if os.path.isfile(xml_file):
        try:
            with open(xml_file, "r", encoding="utf-8") as f:
                old_rss = f.read()
            if rss == old_rss:
                print("No change in RSS content for %s" % sec)
                return
            else:
                os.remove(xml_file)
        except Exception as e:
            print(
                "Error occurred when deleting RSS file %s for %s: %s"
                % (xml_file, sec, str(e))
            )
            return

    try:
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write(rss)
    except Exception as e:
        print(
            "Error occurred when writing RSS file %s for %s: %s"
            % (xml_file, sec, str(e))
        )
        return

    # 更新配置信息并写入文件中
    set_cfg(sec, "md5", new_md5)
    with open("test.ini", "w") as configfile:
        config.write(configfile)


def get_cfg(sec, name):
    return config.get(sec, name).strip('"')


def set_cfg(sec, name, value):
    config.set(sec, name, '"%s"' % value)


def get_cfg_tra(sec, config):
    cc = config.get(sec, "action").strip('"')
    target = ""
    source = ""
    if cc == "auto":
        source = "auto"
        target = "zh-CN"
    else:
        source = cc.split("->")[0]
        target = cc.split("->")[1]
    return source, target


# 读取配置文件
config = configparser.ConfigParser()
config.read("test.ini")

# 获取基础路径
BASE = get_cfg("cfg", "base")
try:
    os.makedirs(BASE)
except:
    pass

# 遍历所有的 RSS 配置，依次更新 RSS 文件
secs = config.sections()

links = []
for x in secs[1:]:
    max_item = int(get_cfg(x, "max"))
    tran(x, max_item)
update_readme(links)

with open("test.ini", "w") as configfile:
    config.write(configfile)
