# merge_adblock.py
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
    
    # 检查是否包含 Google 关键词
    for keyword in GOOGLE_KEYWORDS:
        if keyword in line_lower:
            return True
    
    # 检查是否包含 YouTube 相关域名
    if any(x in line_lower for x in ['.yt', 'youtube', 'googlevideo']):
        return True
    
    return False

def extract_rules(content):
    """提取所有规则"""
    rules = []
    
    # 按行分割
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 检查是否是规则行
        if any(x in line for x in ['DOMAIN', 'URL-REGEX', 'IP-CIDR', 'REJECT', 'PROXY', 'DIRECT']):
            # 如果不包含 Google 关键词，就保留
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
    
    # 去重并排序
    all_rules = list(set(all_rules))
    all_rules.sort()
    
    print(f"\n去重后共 {len(all_rules)} 条规则")
    print(f"已剔除所有 Google/YouTube 相关规则")
    
    # 生成模块文件内容
    module_content = f"""#!name = 广告拦截合集（纯净版）
#!desc = 合并自 fmz200 和 zirawell，已剔除所有 Google/YouTube 规则
#!version = {datetime.now().strftime('%Y.%m.%d')}
#!system = ios

[Rule]
# 自动合并于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 来源1: fmz200/blockAds.module
# 来源2: zirawell/allAdBlock.sgmodule
# 共 {len(all_rules)} 条规则（已剔除 Google/YouTube）

{chr(10).join(all_rules)}

[MITM]
# MITM 主机名（已排除 Google/YouTube）
hostname = %APPEND% 
# 注意：此模块已排除所有 Google/YouTube 域名
# 如需代理 Google/YouTube，请单独添加代理模块

# 确保 YouTube 等不受影响
skip-server = *.googlevideo.com, *.youtube.com, *.googleapis.com, *.ytimg.com, *.ggpht.com, *.gstatic.com
"""
    
    # 写入文件
    file_path = 'adblock_clean.module'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(module_content)
    
    print(f"\n✅ 完成！已保存到 {file_path}")
    print(f"文件绝对路径: {os.path.abspath(file_path)}")
    
    # 打印统计信息
    print(f"\n规则统计：")
    print(f"  总规则数: {len(all_rules)}")
    
    # 按类型统计
    domain_rules = [r for r in all_rules if 'DOMAIN' in r]
    ip_rules = [r for r in all_rules if 'IP-CIDR' in r]
    regex_rules = [r for r in all_rules if 'URL-REGEX' in r]
    
    print(f"  域名规则: {len(domain_rules)}")
    print(f"  IP规则: {len(ip_rules)}")
    print(f"  正则规则: {len(regex_rules)}")

if __name__ == '__main__':
    main()
