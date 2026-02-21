import requests
import re
import os
from datetime import datetime

# 两个模块的URL
URL1 = "https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module"
URL2 = "https://raw.githubusercontent.com/zirawell/R-Store/main/Rule/Surge/Adblock/All/allAdBlock.sgmodule"

# Google相关关键词
GOOGLE_KEYWORDS = ['google', 'youtube', 'googlevideo', 'ggpht', 'ytimg', 
                   'android', 'gstatic', 'googleapis', 'googleusercontent']

def download_file(url):
    """下载文件内容"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return None

def extract_rules(content):
    """从内容中提取规则"""
    rules = []
    if not content:
        return rules
    
    in_rule_section = False
    for line in content.split('\n'):
        line = line.strip()
        
        # 检查是否进入 [Rule] 部分
        if line == '[Rule]':
            in_rule_section = True
            continue
        
        # 如果进入规则部分，提取规则
        if in_rule_section:
            if line and not line.startswith('#'):
                # 规则结束的判断（遇到新的部分或空行）
                if line.startswith('['):
                    break
                rules.append(line)
    
    return rules

def is_google_rule(rule):
    """判断是否与Google相关"""
    rule_lower = rule.lower()
    return any(keyword in rule_lower for keyword in GOOGLE_KEYWORDS)

def create_module_header(rules_count):
    """创建模块头部"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""#!name=合并-广告拦截合集(无Google版)
#!desc=自动合并两个去广告模块，已剔除Google相关规则。\n#!desc=原始模块：blockAds.module + allAdBlock.sgmodule\n#!desc=最后更新：{now} | 规则数量：{rules_count}
#!author=自定义自动构建
#!tag=去广告
#!basedOn=iOS
#!surge_version=5.14.2

[Rule]
"""

def main():
    print(f"开始更新过滤规则 - {datetime.now()}")
    
    # 下载两个文件
    content1 = download_file(URL1)
    content2 = download_file(URL2)
    
    if not content1 and not content2:
        print("错误：无法下载任何文件")
        return
    
    # 提取规则
    rules1 = extract_rules(content1) if content1 else []
    rules2 = extract_rules(content2) if content2 else []
    
    print(f"模块1规则数: {len(rules1)}")
    print(f"模块2规则数: {len(rules2)}")
    
    # 合并并过滤
    all_rules = rules1 + rules2
    filtered_rules = [rule for rule in all_rules if not is_google_rule(rule)]
    
    # 去重
    seen = set()
    unique_rules = []
    for rule in filtered_rules:
        if rule not in seen:
            seen.add(rule)
            unique_rules.append(rule)
    
    print(f"过滤后规则数: {len(unique_rules)}")
    print(f"移除了 {len(all_rules) - len(unique_rules)} 条规则")
    
    # 生成新模块
    header = create_module_header(len(unique_rules))
    content = header + '\n'.join(unique_rules)
    
    # 写入文件
    with open('My_AdBlock_No_Google.sgmodule', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"新模块已生成，规则数: {len(unique_rules)}")
    
    # 可选：生成一个状态文件
    with open('latest_status.txt', 'w', encoding='utf-8') as f:
        f.write(f"最后更新: {datetime.now()}\n")
        f.write(f"模块1规则: {len(rules1)}\n")
        f.write(f"模块2规则: {len(rules2)}\n")
        f.write(f"过滤后规则: {len(unique_rules)}\n")
        f.write(f"移除规则: {len(all_rules) - len(unique_rules)}")

if __name__ == "__main__":
    main()
