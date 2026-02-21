# extract_fliggy.py
# 从两位作者的源文件中提取飞猪广告规则

import requests
import re
from datetime import datetime

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

# 飞猪相关关键词
FLIGGY_KEYWORDS = [
    'fliggy',
    'alitrip',
    'taobaotrip',
    '飞猪',
    'mtop\\.fliggy',
    'trip\\.com.*ad'
]

def extract_fliggy_rules(content):
    """从内容中提取包含飞猪关键词的行"""
    rules = []
    for line in content.split('\n'):
        line_lower = line.lower()
        for keyword in FLIGGY_KEYWORDS:
            if keyword in line_lower or re.search(keyword, line_lower):
                if line.strip() and not line.startswith('#'):
                    rules.append(line.strip())
                break
    return rules

def main():
    all_rules = []
    
    for source in SOURCES:
        try:
            print(f"正在从 {source['name']} 获取规则...")
            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            
            rules = extract_fliggy_rules(response.text)
            print(f"  提取到 {len(rules)} 条规则")
            all_rules.extend(rules)
            
        except Exception as e:
            print(f"  失败: {e}")
    
    # 去重
    all_rules = list(set(all_rules))
    all_rules.sort()
    
    # 生成模块文件
    module_content = f"""#!name = 飞猪广告拦截（每日自动更新）
#!desc = 自动同步自 fmz200 和 zirawell 两位作者的源文件
#!version = {datetime.now().strftime('%Y.%m.%d')}
#!system = ios

[Rule]
# 自动提取于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 共 {len(all_rules)} 条规则

{chr(10).join(all_rules)}

[MITM]
# MITM 主机名（自动提取自规则）
hostname = %APPEND% *.fliggy.com, *.alitrip.com, *.taobaotrip.com

# 确保 YouTube 等不受影响
skip-server = *.googlevideo.com, *.youtube.com, *.googleapis.com
"""
    
    with open('fliggy.module', 'w', encoding='utf-8') as f:
        f.write(module_content)
    
    print(f"\n✅ 完成！共提取 {len(all_rules)} 条去重规则")
    print(f"已保存到 fliggy.module")

if __name__ == '__main__':
    main()
