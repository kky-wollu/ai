#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
from datetime import datetime
import os
import sys

# 配置
SOURCE_URL = "https://raw.githubusercontent.com/kky-wollu/ai/refs/heads/v5/My_AdBlock_No_Google.sgmodule"
OUTPUT_FILE = "Universal_AdBlock.sgmodule"

def debug_print(msg):
    """打印调试信息并强制刷新"""
    print(f"[DEBUG] {msg}")
    sys.stdout.flush()

def fetch_source_content():
    """获取原始模块内容"""
    try:
        debug_print(f"正在获取源文件: {SOURCE_URL}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(SOURCE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        debug_print(f"✅ 源文件获取成功，大小: {len(response.text)} 字节")
        return response.text
    except Exception as e:
        debug_print(f"❌ 获取源文件失败: {e}")
        return None

def extract_rules(content):
    """精确提取[Rule]部分的内容，保持原样"""
    if not content:
        return ""
    
    # 查找[Rule]部分
    rule_match = re.search(r'\[Rule\](.*?)(?=\n\[|$)', content, re.DOTALL)
    if rule_match:
        rules = rule_match.group(1).strip()
        # 保持原格式，只过滤空行
        rules_lines = [line.rstrip() for line in rules.split('\n') if line.strip()]
        debug_print(f"✅ 提取到 {len(rules_lines)} 条源规则")
        
        # 显示几种不同格式的示例
        sample_rules = rules_lines[:5]
        debug_print("源规则格式示例:")
        for i, rule in enumerate(sample_rules, 1):
            debug_print(f"  {i}. {rule}")
        
        return '\n'.join(rules_lines)
    
    debug_print("⚠️ 未找到[Rule]部分")
    return ""

def convert_custom_rule_to_source_format(rule):
    """将自定义规则转换为原始模块的格式"""
    rule = rule.strip()
    if not rule or rule.startswith('#'):
        return rule
    
    # 处理不同类型的规则
    if rule.startswith('DOMAIN-SUFFIX,'):
        # 将 DOMAIN-SUFFIX 转换为 DOMAIN（原始模块的格式）
        domain = rule.replace('DOMAIN-SUFFIX,', '').split(',')[0]
        action = rule.split(',')[-1]
        
        # 根据 action 决定是否添加额外参数
        if action == 'REJECT-TINYGIF':
            return f"DOMAIN,{domain},REJECT,pre-matching,extended-matching"
        else:
            return f"DOMAIN,{domain},REJECT"
    
    # 其他类型的规则保持不变
    return rule

def get_custom_rules():
    """获取并转换自定义规则"""
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
    
    # 转换每条自定义规则
    converted_rules = []
    original_count = 0
    converted_count = 0
    
    for line in custom_rules.split('\n'):
        if line.strip() and not line.startswith('#'):
            original_count += 1
            converted_line = convert_custom_rule_to_source_format(line)
            converted_rules.append(converted_line)
            if converted_line != line:
                converted_count += 1
        else:
            converted_rules.append(line)  # 保留注释和空行
    
    debug_print(f"✅ 自定义规则: 原始 {original_count} 条，转换 {converted_count} 条")
    
    # 显示转换示例
    debug_print("自定义规则转换示例:")
    example_shown = 0
    for i, line in enumerate(custom_rules.split('\n')):
        if line.strip() and not line.startswith('#') and example_shown < 3:
            converted = convert_custom_rule_to_source_format(line)
            debug_print(f"  原始: {line}")
            debug_print(f"  转换: {converted}")
            example_shown += 1
    
    return '\n'.join(converted_rules)

def generate_new_module(source_rules, custom_rules):
    """生成新的模块文件，保持原始模块的格式"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 分离注释和规则
    source_lines = source_rules.split('\n') if source_rules else []
    custom_lines = custom_rules.split('\n')
    
    # 去重（只对非注释行去重）
    seen_rules = set()
    all_lines = []
    
    # 先添加源规则
    for line in source_lines:
        if line.strip() and not line.startswith('#'):
            if line not in seen_rules:
                seen_rules.add(line)
                all_lines.append(line)
        else:
            all_lines.append(line)
    
    # 再添加自定义规则（已转换格式）
    for line in custom_lines:
        if line.strip() and not line.startswith('#'):
            if line not in seen_rules:
                seen_rules.add(line)
                all_lines.append(line)
        elif line.startswith('#'):
            all_lines.append(line)
    
    # 统计
    rule_count = len([l for l in all_lines if l.strip() and not l.startswith('#')])
    comment_count = len([l for l in all_lines if l.startswith('#')])
    
    debug_print(f"📊 最终合并: {rule_count} 条规则, {comment_count} 条注释")
    
    header = f"""#!name=Universal Ad Vendors Block
#!desc=通用广告服务商/竞价平台/统计埋点拦截（偏保守，降低误杀）
#!desc=• 基于原始模块：My_AdBlock_No_Google
#!desc=• 合并自定义规则
#!desc=• 最后更新：{now}
#!desc=• 规则总数：{rule_count}
#!author=Xiaochuan
#!category=AdBlock

[Rule]
"""
    return header + '\n'.join(all_lines), rule_count

def main():
    print("=" * 60)
    print("🚀 开始更新广告拦截模块")
    print("=" * 60)
    sys.stdout.flush()
    
    # 获取源内容
    source_content = fetch_source_content()
    if not source_content:
        debug_print("❌ 无法获取源文件")
        return 1
    
    # 提取规则
    source_rules = extract_rules(source_content)
    
    # 获取并转换自定义规则
    custom_rules = get_custom_rules()
    
    # 生成新模块
    debug_print("🔄 正在合并规则...")
    new_module, rule_count = generate_new_module(source_rules, custom_rules)
    
    # 保存文件
    output_path = os.path.join(os.getcwd(), OUTPUT_FILE)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_module)
        debug_print(f"✅ 文件保存成功: {output_path}")
    except Exception as e:
        debug_print(f"❌ 文件保存失败: {e}")
        return 1
    
    # 验证文件
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        debug_print(f"📦 文件大小：{file_size} 字节")
        
        # 显示混合后的格式示例
        with open(output_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        debug_print("\n📋 最终文件格式示例（混合效果）:")
        rule_examples = []
        for line in lines:
            if line.startswith('DOMAIN,') or line.startswith('AND,') or line.startswith('URL-REGEX,'):
                rule_examples.append(line.strip())
                if len(rule_examples) >= 5:
                    break
        
        for i, rule in enumerate(rule_examples, 1):
            debug_print(f"  {i}. {rule}")
    
    print("=" * 60)
    print(f"✅ 成功！生成模块: {OUTPUT_FILE}")
    print(f"📊 总规则数：{rule_count}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
