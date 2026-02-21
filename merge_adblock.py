name: 每日合并纯净广告规则

on:
  schedule:
    - cron: '0 18 * * *'
  workflow_dispatch:

jobs:
  update-rules:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    
    steps:
      - name: 检出仓库代码
        uses: actions/checkout@v3
      
      - name: 设置 Python 环境
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: 安装依赖
        run: pip install requests
      
      - name: 运行合并脚本
        run: python merge_adblock.py
      
      - name: 提交更新
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add adblock_clean.module
          git diff --staged --quiet || git commit -m "自动合并广告规则 $(date +'%Y-%m-%d')"
          git push
