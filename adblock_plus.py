# adblock_plus.py
# 合并两位作者的广告模块，并剔除 Google/YouTube 规则

import requests
import re
from datetime import datetime
import os

# 源文件地址
SOURCES = [
    {
        'name': 'fmz200',
        'url': 'https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module'
    },
    {
        'name': 'zirawell',
        'url': 'https://raw.githubusercontent.com/zirawell/R-Store/main/Rule/Surge/Adblock/All/allAdBlock.sgmodule'
    }
]

# 需要剔除的 Google/YouTube 相关关键词
GOOGLE_KEYWORDS = [
    'google',
    'youtube',
    'googlevideo',
    'ytimg',
    'ggpht',
    'gstatic',
    'googleapis',
    'youtu.be',
    'googlead',
    'doubleclick',
    'gmail',
    'android',
    'chrome',
    'blogger',
    'blogspot'
]

def should_exclude(line):
    """判断是否应该排除该规则"""
    line_lower = line.lower()
    
    for keyword in GOOGLE_KEYWORDS:
        if keyword in line_lower:
            return True
    return False

def extract_rules(content):
    """提取所有规则"""
    rules = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if any(x in line for x in ['DOMAIN', 'URL-REGEX', 'IP-CIDR', 'REJECT']):
            if not should_exclude(line):
                rules.append(line)
    
    return rules

def main():
    print("开始合并广告规则...")
    all_rules = []
    
    for source in SOURCES:
        try:
            print(f"正在从 {source['name']} 获取规则...")
            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            
            rules = extract_rules(response.text)
            print(f"  提取到 {len(rules)} 条规则")
            all_rules.extend(rules)
            
        except Exception as e:
            print(f"  失败: {e}")
    
    all_rules = list(set(all_rules))
    all_rules.sort()
    
    module_content = f"""#!name = AdBlock Plus 纯净版
#!desc = 合并自 fmz200 和 zirawell，已剔除 Google/YouTube
#!version = {datetime.now().strftime('%Y.%m.%d')}
#!system = ios

[Rule]
# 自动合并于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 共 {len(all_rules)} 条规则

{chr(10).join(all_rules)}

[MITM]
hostname = %APPEND% 
skip-server = *.googlevideo.com, *.youtube.com, *.googleapis.com, *.ytimg.com, *.ggpht.com, *.gstatic.com
"""
    
    with open('adblock_plus.module', 'w', encoding='utf-8') as f:
        f.write(module_content)
    
    print(f"\n✅ 完成！共 {len(all_rules)} 条规则")
    print(f"已保存到 adblock_plus.module")

if __name__ == '__main__':
    main()
