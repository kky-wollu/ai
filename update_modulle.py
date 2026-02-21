import requests
import re
from datetime import datetime
import os

# 配置
SOURCE_URL = "https://raw.githubusercontent.com/kky-wollu/ai/refs/heads/v5/My_AdBlock_No_Google.sgmodule"
OUTPUT_FILE = "Universal_AdBlock.sgmodule"

def fetch_source_content():
    """获取原始模块内容"""
    try:
        print(f"正在获取源文件: {SOURCE_URL}")
        response = requests.get(SOURCE_URL)
        response.raise_for_status()
        print("✅ 源文件获取成功")
        return response.text
    except Exception as e:
        print(f"❌ 获取源文件失败: {e}")
        return None

def extract_rules(content):
    """提取[Rule]部分的内容"""
    rule_match = re.search(r'\[Rule\](.*?)(?=\n\[|$)', content, re.DOTALL)
    if rule_match:
        rules = rule_match.group(1).strip()
        # 过滤掉空行和注释行
        rules_lines = [line.strip() for line in rules.split('\n') 
                      if line.strip() and not line.strip().startswith('#')]
        print(f"✅ 提取到 {len(rules_lines)} 条源规则")
        return '\n'.join(rules_lines)
    print("⚠️ 未找到[Rule]部分")
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
    
    custom_lines = [line.strip() for line in custom_rules.split('\n') if line.strip()]
    print(f"✅ 加载到 {len(custom_lines)} 条自定义规则")
    return custom_rules

def generate_new_module(source_rules, custom_rules):
    """生成新的模块文件"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 合并规则
    if source_rules:
        all_rules = source_rules + '\n' + custom_rules
    else:
        all_rules = custom_rules
    
    # 去重（但保留注释）
    rule_lines = []
    seen_rules = set()
    
    for line in all_rules.split('\n'):
        line = line.rstrip()
        if line.startswith('#') or not line:
            rule_lines.append(line)
        elif line not in seen_rules:
            seen_rules.add(line)
            rule_lines.append(line)
    
    merged_rules = '\n'.join(rule_lines)
    
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
    print("=" * 50)
    print("🚀 开始更新广告拦截模块")
    print("=" * 50)
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    print(f"📁 当前工作目录: {current_dir}")
    
    # 获取源内容
    source_content = fetch_source_content()
    if not source_content:
        print("❌ 无法获取源文件，退出程序")
        return
    
    # 提取规则
    source_rules = extract_rules(source_content)
    
    # 获取自定义规则
    custom_rules = get_custom_rules()
    
    # 生成新模块
    print("🔄 正在合并规则...")
    new_module = generate_new_module(source_rules, custom_rules)
    
    # 统计规则数量
    rule_count = len([line for line in new_module.split('\n') 
                     if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('[Rule]')])
    
    # 保存文件
    output_path = os.path.join(current_dir, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_module)
    
    print(f"✅ 模块生成成功！")
    print(f"📊 总规则数：{rule_count}")
    print(f"📁 输出文件：{output_path}")
    
    # 验证文件是否存在
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"📦 文件大小：{file_size} 字节")
    else:
        print("⚠️ 警告：文件可能未成功保存")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
