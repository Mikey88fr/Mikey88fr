#!/usr/bin/env python3
"""
Optimized Knowledge Base Builder for 7B LLMs
Focuses on essential repositories for Telegram and Matrix bot development
"""

import os
import sys
from github_knowledge_builder import generate_repo_knowledge_file

def main():
    # Paths
    source_base = r"C:\Users\Bills\Projects\REPO _KNOWLEDGE"
    output_dir = r"C:\Users\Bills\Projects\ai_knowledge_output_files"
    
    # Essential repositories for 7B models (prioritized for maximum learning efficiency)
    essential_repos = {
        "telegram_bot_essential": [
            {
                "path": "python-telegram-bot-master",
                "name": "Python_Telegram_Bot_Essential",
                "priority": "CRITICAL",
                "max_size_kb": 800  # Larger for the main library
            },
            {
                "path": "aiogram-dev-3.x", 
                "name": "Aiogram_Async_Bot_Essential",
                "priority": "CRITICAL",
                "max_size_kb": 600
            },
            {
                "path": "telegram-bot-design-pattern-master",
                "name": "Telegram_Design_Patterns",
                "priority": "HIGH",
                "max_size_kb": 400
            }
        ],
        "matrix_bot_essential": [
            {
                "path": "matrix-nio-main",
                "name": "Matrix_Nio_Python_Essential", 
                "priority": "CRITICAL",
                "max_size_kb": 700
            },
            {
                "path": "matrix-bot-sdk-main",
                "name": "Matrix_Bot_SDK_JS_Essential",
                "priority": "CRITICAL", 
                "max_size_kb": 600
            },
            {
                "path": "matrix-spec-main",
                "name": "Matrix_Protocol_Spec_Essential",
                "priority": "CRITICAL",
                "max_size_kb": 500
            },
            {
                "path": "matrix-appservice-bridge-develop",
                "name": "Matrix_Bridge_Patterns",
                "priority": "HIGH",
                "max_size_kb": 400
            }
        ]
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 OPTIMIZED KNOWLEDGE BASE BUILDER FOR 7B LLMs")
    print("=" * 60)
    print(f"Source: {source_base}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    total_processed = 0
    
    for category, repos in essential_repos.items():
        print(f"\n📚 Processing {category.upper().replace('_', ' ')}...")
        print("-" * 40)
        
        for repo_config in repos:
            repo_path = os.path.join(source_base, repo_config["path"])
            
            if not os.path.isdir(repo_path):
                print(f"❌ MISSING: {repo_config['path']}")
                continue
                
            print(f"⚡ {repo_config['priority']} - Processing {repo_config['name']}...")
            
            try:
                generate_repo_knowledge_file(
                    repo_path=repo_path,
                    output_dir=output_dir,
                    max_output_size_kb=repo_config["max_size_kb"],
                    max_file_size_kb=100  # Larger individual files for essential repos
                )
                total_processed += 1
                print(f"✅ Completed {repo_config['name']}")
                
            except Exception as e:
                print(f"❌ Error processing {repo_config['name']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎉 OPTIMIZATION COMPLETE!")
    print(f"📊 Processed {total_processed} essential repositories")
    print(f"📁 Knowledge files saved to: {output_dir}")
    print("=" * 60)
    
    # Print summary of what was created
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.md')]
        total_size_mb = sum(os.path.getsize(os.path.join(output_dir, f)) for f in files) / (1024 * 1024)
        print(f"\n📈 SUMMARY:")
        print(f"   • {len(files)} knowledge files created")
        print(f"   • Total size: {total_size_mb:.1f} MB")
        print(f"   • Optimized for 7B model constraints")
        print(f"   • Focus: Essential bot development patterns")

if __name__ == "__main__":
    main()
