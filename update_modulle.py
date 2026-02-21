import requests
import re
from datetime import datetime
import os

# 配置
SOURCE_URL = "https://raw.githubusercontent.com/kky-wollu/ai/refs/heads/v5/My_AdBlock_No_Google.sgmodule"
OUTPUT_FILE = "Universal_AdBlock.sgmodule"
CUSTOM_RULES_FILE = "custom_rules.txt"  # 存储你提供的自定义规则

def fetch_source_content():
    """获取原始模块内容"""
    try:
        response = requests.get(SOURCE_URL)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"获取源文件失败: {e}")
        return None

def extract_rules(content):
    """提取[Rule]部分的内容"""
    rule_match = re.search(r'\[Rule\](.*?)(?=\n\[|$)', content, re.DOTALL)
    if rule_match:
        rules = rule_match.group(1).strip()
        # 过滤掉空行和注释行
        rules_lines = [line.strip() for line in rules.split('\n') 
                      if line.strip() and not line.strip().startswith('#')]
        return '\n'.join(rules_lines)
    return ""

def get_custom_rules():
    """获取你提供的自定义规则"""
    custom_rules = """# =========================
# 1) 国内常见广告/竞价平台
# =========================

# Tencent GDT / 广点通
DOMAIN-SUFFIX,gdt.qq.com,REJECT
DOMAIN-SUFFIX,e.qq.com,REJECT

# 1RTB
DOMAIN-SUFFIX,1rtb.com,REJECT
DOMAIN-SUFFIX,1rtb.net,REJECT

# 穿山甲/巨量（Bytedance）
DOMAIN-SUFFIX,pangle.io,REJECT
DOMAIN-SUFFIX,ctobsnssdk.com,REJECT
DOMAIN-SUFFIX,byteoversea.com,REJECT

# 快手广告
DOMAIN-SUFFIX,kuaishou.com,REJECT
DOMAIN-SUFFIX,ksadks.com,REJECT
DOMAIN-SUFFIX,e.kuaishou.com,REJECT

# 百度联盟/统计（保守拦常见前缀域）
DOMAIN-SUFFIX,baidu.com,REJECT-TINYGIF
DOMAIN-SUFFIX,bdstatic.com,REJECT-TINYGIF

# 友盟/阿里统计
DOMAIN-SUFFIX,umeng.com,REJECT
DOMAIN-SUFFIX,umengcloud.com,REJECT

# TalkingData
DOMAIN-SUFFIX,talkingdata.com,REJECT

# AppsFlyer / Adjust / Branch / Kochava / Firebase 归因&追踪
DOMAIN-SUFFIX,appsflyer.com,REJECT
DOMAIN-SUFFIX,adjust.com,REJECT
DOMAIN-SUFFIX,branch.io,REJECT
DOMAIN-SUFFIX,kochava.com,REJECT
DOMAIN-SUFFIX,app-measurement.com,REJECT
DOMAIN-SUFFIX,google-analytics.com,REJECT

# =========================
# 2) 国外常见广告网络
# =========================

# Google Ads/DoubleClick/AdServices
DOMAIN-SUFFIX,doubleclick.net,REJECT
DOMAIN-SUFFIX,googlesyndication.com,REJECT
DOMAIN-SUFFIX,googleadservices.com,REJECT
DOMAIN-SUFFIX,adservice.google.com,REJECT

# Meta (Facebook) Ads/Analytics
DOMAIN-SUFFIX,facebook.com,REJECT-TINYGIF
DOMAIN-SUFFIX,facebook.net,REJECT-TINYGIF

# Unity Ads / Vungle / AppLovin / IronSource / Chartboost / InMobi
DOMAIN-SUFFIX,unityads.unity3d.com,REJECT
DOMAIN-SUFFIX,ads.vungle.com,REJECT
DOMAIN-SUFFIX,applovin.com,REJECT
DOMAIN-SUFFIX,ironsrc.com,REJECT
DOMAIN-SUFFIX,chartboost.com,REJECT
DOMAIN-SUFFIX,inmobi.com,REJECT

# MoPub (旧)/Rubicon/Taboola/Outbrain
DOMAIN-SUFFIX,rubiconproject.com,REJECT
DOMAIN-SUFFIX,taboola.com,REJECT
DOMAIN-SUFFIX,outbrain.com,REJECT"""
    return custom_rules

def generate_new_module(source_rules, custom_rules):
    """生成新的模块文件"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 合并规则（去重）
    all_rules = source_rules + '\n' + custom_rules
    rules_set = set(all_rules.split('\n'))
    merged_rules = '\n'.join(sorted(rules_set))
    
    header = f"""#!name=Universal Ad Vendors Block
#!desc=通用广告服务商/竞价平台/统计埋点拦截（偏保守，降低误杀）
#!desc=• 基于原始模块：My_AdBlock_No_Google
#!desc=• 合并自定义规则
#!desc=• 最后更新：{now}
#!author=Xiaochuan
#!category=AdBlock

[Rule]
"""
    return header + merged_rules

def main():
    print("开始更新模块...")
    
    # 获取源内容
    source_content = fetch_source_content()
    if not source_content:
        return
    
    # 提取规则
    source_rules = extract_rules(source_content)
    source_rule_count = len(source_rules.split('\n'))
    print(f"从源模块提取到 {source_rule_count} 条规则")
    
    # 获取自定义规则
    custom_rules = get_custom_rules()
    custom_rule_count = len(custom_rules.split('\n'))
    print(f"自定义规则 {custom_rule_count} 条")
    
    # 生成新模块
    new_module = generate_new_module(source_rules, custom_rules)
    total_rules = len(new_module.split('\n')) - 4  # 减去header行数
    
    # 保存文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_module)
    
    print(f"✅ 模块生成成功！")
    print(f"📊 总规则数：{total_rules}")
    print(f"📁 输出文件：{OUTPUT_FILE}")

if __name__ == "__main__":
    main()
