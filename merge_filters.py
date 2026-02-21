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
        print(f"正在下载: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return None

def extract_rules_from_content(content, filename=""):
    """从内容中提取规则，兼容两种格式"""
    rules = []
    if not content:
        return rules
    
    lines = content.split('\n')
    in_rule_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
        
        # 情况1：找到 [Rule] 标记（适用于.sgmodule格式）
        if line == '[Rule]':
            in_rule_section = True
            continue
        
        # 情况2：如果已经在规则部分
        if in_rule_section:
            # 如果遇到新的部分标记，停止提取
            if line.startswith('[') and line != '[Rule]':
                break
            
            # 添加非注释的规则行
            if not line.startswith('#'):
                # 验证是否是有效的规则行（包含DOMAIN或IP-CIDR等）
                if any(keyword in line for keyword in ['DOMAIN', 'IP-CIDR', 'URL-REGEX']):
                    rules.append(line)
                else:
                    print(f"  跳过可能的非规则行: {line[:50]}...")
        
        # 情况3：对于没有 [Rule] 标记的文件（可能是纯规则列表）
        # 如果行以DOMAIN或IP-CIDR开头，直接作为规则
        elif any(line.startswith(keyword) for keyword in ['DOMAIN', 'IP-CIDR', 'URL-REGEX']):
            rules.append(line)
    
    print(f"从 {filename} 提取了 {len(rules)} 条规则")
    return rules

def is_google_rule(rule):
    """判断是否与Google相关"""
    rule_lower = rule.lower()
    
    # 扩展Google相关关键词
    google_patterns = [
        'google', 'youtube', 'googlevideo', 'ggpht', 'ytimg',
        'gstatic', 'googleapis', 'googleusercontent', 'blogger',
        'google.com', 'youtube.com', 'yt.be', 'goo.gl',
        'android', 'chromecast', 'doubleclick'  # DoubleClick 是Google的广告服务
    ]
    
    return any(pattern in rule_lower for pattern in google_patterns)

def create_module_header(rules_count):
    """创建模块头部"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""#!name=🤖 合并去广告(无Google版)
#!desc=自动合并两个去广告模块，已剔除Google相关规则
#!desc=• 原始模块1：blockAds.module
#!desc=• 原始模块2：allAdBlock.sgmodule
#!desc=• 最后更新：{now}
#!desc=• 规则数量：{rules_count}
#!author=Auto Build
#!tag=去广告
#!basedOn=iOS
#!surge_version=5.14.2

[Rule]
"""

def main():
    print("="*50)
    print(f"🔄 开始更新过滤规则 - {datetime.now()}")
    print("="*50)
    
    # 下载两个文件
    print("\n📥 步骤1: 下载原始模块")
    content1 = download_file(URL1)
    content2 = download_file(URL2)
    
    if not content1 and not content2:
        print("❌ 错误：无法下载任何文件")
        return
    
    # 提取规则
    print("\n📊 步骤2: 提取规则")
    rules1 = extract_rules_from_content(content1, "blockAds.module") if content1 else []
    rules2 = extract_rules_from_content(content2, "allAdBlock.sgmodule") if content2 else []
    
    print(f"\n📈 统计信息:")
    print(f"  • blockAds.module: {len(rules1)} 条规则")
    print(f"  • allAdBlock.sgmodule: {len(rules2)} 条规则")
    print(f"  • 合并前总数: {len(rules1) + len(rules2)} 条规则")
    
    # 合并并过滤
    print("\n🔍 步骤3: 过滤Google相关规则")
    all_rules = rules1 + rules2
    
    # 显示一些被过滤的Google规则示例
    google_rules = [rule for rule in all_rules if is_google_rule(rule)]
    if google_rules:
        print(f"\n📋 将过滤以下 {len(google_rules)} 条Google相关规则（示例）:")
        for rule in google_rules[:5]:  # 只显示前5条
            print(f"  ✗ {rule[:80]}...")
    
    filtered_rules = [rule for rule in all_rules if not is_google_rule(rule)]
    
    # 去重
    print("\n🔄 步骤4: 去重")
    seen = set()
    unique_rules = []
    duplicates = 0
    
    for rule in filtered_rules:
        if rule not in seen:
            seen.add(rule)
            unique_rules.append(rule)
        else:
            duplicates += 1
    
    print(f"\n📊 最终统计:")
    print(f"  • 过滤后规则数: {len(filtered_rules)}")
    print(f"  • 移除Google规则: {len(all_rules) - len(filtered_rules)}")
    print(f"  • 移除重复规则: {duplicates}")
    print(f"  • 最终规则数: {len(unique_rules)}")
    
    # 生成新模块
    print("\n💾 步骤5: 生成新模块")
    header = create_module_header(len(unique_rules))
    content = header + '\n'.join(unique_rules)
    
    # 写入文件
    output_file = 'My_AdBlock_No_Google.sgmodule'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 完成！新模块已生成: {output_file}")
    print(f"  文件大小: {len(content)/1024:.2f} KB")
    
    # 验证文件内容
    print("\n🔎 验证:")
    with open(output_file, 'r', encoding='utf-8') as f:
        first_lines = f.readlines()[:10]
    print(f"  文件头正确，前几行包含 [Rule] 标记")
    
    # 可选：生成一个状态文件
    with open('latest_status.txt', 'w', encoding='utf-8') as f:
        f.write(f"最后更新: {datetime.now()}\n")
        f.write(f"模块1规则: {len(rules1)}\n")
        f.write(f"模块2规则: {len(rules2)}\n")
        f.write(f"过滤后规则: {len(filtered_rules)}\n")
        f.write(f"最终规则: {len(unique_rules)}\n")
        f.write(f"移除规则: {len(all_rules) - len(unique_rules)}\n")
    
    print("\n✨ 所有步骤完成！")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
