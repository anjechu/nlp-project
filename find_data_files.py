#!/usr/bin/env python3
"""
数据文件查找工具 - Data File Finder Utility

用途: 帮助用户找到JSON数据文件的位置
Usage: Helps users locate JSON data files

运行方式:
    python find_data_files.py
    python find_data_files.py --pattern "steam_reviews_*.json"
"""

import os
import glob
import argparse


def find_all_json_files(base_dir='.', max_depth=3):
    """
    递归查找所有JSON文件
    
    Args:
        base_dir: 起始目录
        max_depth: 最大搜索深度
    
    Returns:
        按目录分组的JSON文件列表
    """
    json_files = {}
    
    for depth in range(max_depth + 1):
        if depth == 0:
            pattern = os.path.join(base_dir, '*.json')
        elif depth == 1:
            pattern = os.path.join(base_dir, '*', '*.json')
        elif depth == 2:
            pattern = os.path.join(base_dir, '*', '*', '*.json')
        else:
            pattern = os.path.join(base_dir, '*', '*', '*', '*.json')
        
        files = glob.glob(pattern)
        for f in files:
            dir_name = os.path.dirname(f)
            if dir_name not in json_files:
                json_files[dir_name] = []
            json_files[dir_name].append(os.path.basename(f))
    
    return json_files


def main():
    parser = argparse.ArgumentParser(description='查找JSON数据文件')
    parser.add_argument('--pattern', type=str, default='*.json',
                       help='文件匹配模式 (默认: *.json)')
    parser.add_argument('--base-dir', type=str, default='.',
                       help='搜索起始目录 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📂 数据文件查找工具 - Data File Finder")
    print("="*70)
    print(f"\n🔍 搜索目录: {os.path.abspath(args.base_dir)}")
    print(f"🔍 匹配模式: {args.pattern}\n")
    
    # 查找所有JSON文件
    json_files = find_all_json_files(args.base_dir)
    
    if not json_files:
        print("❌ 未找到任何JSON文件！\n")
        print("💡 建议:")
        print("   1. 检查当前目录是否正确")
        print("   2. 确认数据文件已下载/爬取")
        print("   3. 使用 --base-dir 参数指定其他目录")
        return
    
    print(f"✅ 找到 {sum(len(files) for files in json_files.values())} 个JSON文件\n")
    print("📁 按目录分组:")
    print("-" * 70)
    
    for dir_path, files in sorted(json_files.items()):
        rel_path = os.path.relpath(dir_path, args.base_dir)
        if rel_path == '.':
            rel_path = '当前目录'
        
        print(f"\n📂 {rel_path}/ ({len(files)} 个文件)")
        
        # 显示文件名
        for i, filename in enumerate(sorted(files), 1):
            print(f"   {i}. {filename}")
            
            # 如果文件数量较多，只显示前5个
            if i == 5 and len(files) > 5:
                print(f"   ... 还有 {len(files) - 5} 个文件")
                break
    
    print("\n" + "="*70)
    print("💡 使用建议:")
    print("="*70)
    
    # 生成使用建议
    for dir_path, files in sorted(json_files.items()):
        rel_path = os.path.relpath(dir_path, args.base_dir)
        if rel_path == '.':
            # 当前目录的文件
            if len(files) == 1:
                print(f"\n单个文件:")
                print(f"   python train_sentiment.py --data_path {files[0]}")
            else:
                print(f"\n多个文件 (使用通配符):")
                print(f"   python train_sentiment.py --data_path '*.json'")
        else:
            # 子目录的文件
            if len(files) == 1:
                print(f"\n{rel_path}/ 中的单个文件:")
                print(f"   python train_sentiment.py --data_path {rel_path}/{files[0]}")
            else:
                print(f"\n{rel_path}/ 中的多个文件:")
                print(f"   python train_sentiment.py --data_path '{rel_path}/*.json'")
        
        # 只显示前2个目录的建议
        if len([d for d in json_files.keys() if d <= dir_path]) >= 2:
            break
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
