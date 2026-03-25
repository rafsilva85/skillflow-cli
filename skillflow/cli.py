#!/usr/bin/env python3
"""
SkillFlow CLI — Search, discover, and install AI agent skills from the terminal.

Usage:
    skillflow search <query>          Search for skills
    skillflow trending                Show trending skills
    skillflow info <skill-id>         Get skill details
    skillflow install <skill-id>      Install a skill
    skillflow categories              List categories
    skillflow publishers              List top publishers
    skillflow --version               Show version
    skillflow --help                  Show help
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

__version__ = "1.0.0"

# Embedded skill catalog (MVP — production would use SkillFlow API)
CATALOG = [
    {
        "id": "credit-optimizer-v5",
        "name": "Credit Optimizer v5",
        "desc": "Optimize Manus AI credit usage — save 30-75% without quality loss",
        "category": "Productivity",
        "publisher": "rafsilva85",
        "trust": 95,
        "tags": ["manus", "optimization", "credits"],
        "url": "https://skillflow.builders/skill/credit-optimizer-v5",
        "github": "https://github.com/rafsilva85/credit-optimizer-v5",
        "raw_url": "https://raw.githubusercontent.com/rafsilva85/credit-optimizer-v5/main/SKILL.md",
        "platforms": ["Manus AI", "Claude Code", "Cursor"],
        "trending": True
    },
    {
        "id": "fast-navigation",
        "name": "Fast Navigation",
        "desc": "Accelerate web navigation by 30-2000x with programmatic toolkit",
        "category": "Development",
        "publisher": "rafsilva85",
        "trust": 92,
        "tags": ["web", "scraping", "performance"],
        "url": "https://skillflow.builders/skill/fast-navigation",
        "github": "https://github.com/rafsilva85/fast-navigation",
        "raw_url": "https://raw.githubusercontent.com/rafsilva85/fast-navigation/main/SKILL.md",
        "platforms": ["Manus AI"],
        "trending": True
    },
    {
        "id": "skill-creator",
        "name": "Skill Creator",
        "desc": "Guide for creating AI agent skills with best practices",
        "category": "Development",
        "publisher": "rafsilva85",
        "trust": 90,
        "tags": ["skills", "creation", "meta"],
        "url": "https://skillflow.builders/skill/skill-creator",
        "github": "",
        "raw_url": "",
        "platforms": ["Manus AI", "Claude Code", "Cursor", "Copilot"],
        "trending": False
    },
    {
        "id": "skill-finder",
        "name": "Skill Finder",
        "desc": "Auto-find and install the best AI skills for any prompt",
        "category": "Productivity",
        "publisher": "rafsilva85",
        "trust": 93,
        "tags": ["search", "discovery", "automation"],
        "url": "https://skillflow.builders/skill/skill-finder",
        "github": "",
        "raw_url": "",
        "platforms": ["Manus AI"],
        "trending": True
    },
    {
        "id": "security-auditor",
        "name": "Security Auditor",
        "desc": "OWASP-based security auditing with actionable fix recommendations",
        "category": "Security",
        "publisher": "community",
        "trust": 91,
        "tags": ["security", "owasp", "audit"],
        "url": "https://skillflow.builders/skill/security-auditor",
        "github": "",
        "raw_url": "",
        "platforms": ["Claude Code", "Cursor", "Copilot"],
        "trending": True
    },
    {
        "id": "docker-compose-gen",
        "name": "Docker Compose Generator",
        "desc": "Generate optimized Docker Compose configs for any stack",
        "category": "DevOps",
        "publisher": "community",
        "trust": 87,
        "tags": ["docker", "devops", "containers"],
        "url": "https://skillflow.builders/skill/docker-compose-gen",
        "github": "",
        "raw_url": "",
        "platforms": ["Claude Code", "Cursor", "Copilot"],
        "trending": False
    },
    {
        "id": "data-viz-expert",
        "name": "Data Visualization Expert",
        "desc": "Create publication-quality visualizations with matplotlib, plotly, D3",
        "category": "Data",
        "publisher": "community",
        "trust": 84,
        "tags": ["data", "visualization", "charts"],
        "url": "https://skillflow.builders/skill/data-viz-expert",
        "github": "",
        "raw_url": "",
        "platforms": ["Manus AI", "Claude Code"],
        "trending": False
    },
    {
        "id": "seo-optimizer",
        "name": "SEO Optimizer",
        "desc": "On-page SEO optimization for web projects",
        "category": "Marketing",
        "publisher": "community",
        "trust": 82,
        "tags": ["seo", "marketing", "web"],
        "url": "https://skillflow.builders/skill/seo-optimizer",
        "github": "",
        "raw_url": "",
        "platforms": ["Manus AI", "Claude Code"],
        "trending": False
    },
]

# Colors
class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    END = "\033[0m"

def no_color():
    """Disable colors if not a TTY"""
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        C.BOLD = C.GREEN = C.BLUE = C.YELLOW = C.RED = C.CYAN = C.DIM = C.END = ""

def print_banner():
    print(f"""
{C.BOLD}{C.CYAN}  ___  _    _  _  _  ___  _                {C.END}
{C.BOLD}{C.CYAN} / __|| |__(_)| || || __|| | ___ __ __ __ {C.END}
{C.BOLD}{C.CYAN} \\__ \\| / /| || || || _| | |/ _ \\\\ V  V / {C.END}
{C.BOLD}{C.CYAN} |___/|_\\_\\|_||_||_||_|  |_|\\___/ \\_/\\_/  {C.END}
{C.DIM} The curated marketplace for AI agent skills{C.END}
{C.DIM} https://skillflow.builders{C.END}
""")

def trust_color(score):
    if score >= 90: return C.GREEN
    if score >= 80: return C.YELLOW
    return C.RED

def cmd_search(args):
    query = " ".join(args.query).lower()
    results = [s for s in CATALOG if 
               query in s["name"].lower() or 
               query in s["desc"].lower() or 
               any(query in t for t in s["tags"]) or
               query in s["category"].lower()]
    
    if not results:
        print(f"\n{C.YELLOW}No skills found for '{query}'.{C.END}")
        print(f"Browse all: {C.BLUE}https://skillflow.builders/explore{C.END}\n")
        return
    
    print(f"\n{C.BOLD}Found {len(results)} skill(s) matching '{query}':{C.END}\n")
    for s in results:
        tc = trust_color(s["trust"])
        trending = f" {C.RED}🔥 TRENDING{C.END}" if s["trending"] else ""
        print(f"  {C.BOLD}{s['name']}{C.END} {C.DIM}({s['id']}){C.END}{trending}")
        print(f"  {s['desc']}")
        print(f"  Trust: {tc}{s['trust']}/100{C.END} | Category: {s['category']} | By: {s['publisher']}")
        print(f"  Platforms: {', '.join(s['platforms'])}")
        print(f"  {C.DIM}skillflow install {s['id']}{C.END}")
        print()

def cmd_trending(args):
    trending = sorted([s for s in CATALOG if s["trending"]], key=lambda x: -x["trust"])
    print(f"\n{C.BOLD}{C.RED}🔥 Trending Skills on SkillFlow{C.END}\n")
    for i, s in enumerate(trending, 1):
        tc = trust_color(s["trust"])
        print(f"  {C.BOLD}{i}. {s['name']}{C.END} {C.DIM}({s['id']}){C.END}")
        print(f"     {s['desc']}")
        print(f"     Trust: {tc}{s['trust']}/100{C.END} | {', '.join(s['platforms'])}")
        print()

def cmd_info(args):
    skill = next((s for s in CATALOG if s["id"] == args.skill_id), None)
    if not skill:
        print(f"\n{C.RED}Skill '{args.skill_id}' not found.{C.END}")
        print(f"Try: {C.DIM}skillflow search <keyword>{C.END}\n")
        return
    
    tc = trust_color(skill["trust"])
    print(f"\n{C.BOLD}{'='*50}{C.END}")
    print(f"{C.BOLD}{C.CYAN}{skill['name']}{C.END}")
    print(f"{C.BOLD}{'='*50}{C.END}\n")
    print(f"  {C.BOLD}ID:{C.END}         {skill['id']}")
    print(f"  {C.BOLD}Trust:{C.END}      {tc}{skill['trust']}/100{C.END}")
    print(f"  {C.BOLD}Category:{C.END}   {skill['category']}")
    print(f"  {C.BOLD}Publisher:{C.END}  {skill['publisher']}")
    print(f"  {C.BOLD}Platforms:{C.END}  {', '.join(skill['platforms'])}")
    print(f"  {C.BOLD}Tags:{C.END}       {', '.join(skill['tags'])}")
    print(f"\n  {C.BOLD}Description:{C.END}")
    print(f"  {skill['desc']}")
    print(f"\n  {C.BOLD}Links:{C.END}")
    print(f"  Marketplace: {C.BLUE}{skill['url']}{C.END}")
    if skill["github"]:
        print(f"  GitHub:      {C.BLUE}{skill['github']}{C.END}")
    print(f"\n  {C.BOLD}Install:{C.END}")
    print(f"  {C.GREEN}skillflow install {skill['id']}{C.END}\n")

def cmd_install(args):
    skill = next((s for s in CATALOG if s["id"] == args.skill_id), None)
    if not skill:
        print(f"\n{C.RED}Skill '{args.skill_id}' not found.{C.END}\n")
        return
    
    if not skill["raw_url"]:
        print(f"\n{C.YELLOW}This skill is available on the SkillFlow marketplace.{C.END}")
        print(f"Visit: {C.BLUE}{skill['url']}{C.END}\n")
        return
    
    # Determine install directory
    install_dir = Path.home() / ".manus" / "skills" / skill["id"]
    
    # Check for common skill directories
    for candidate in [
        Path.home() / ".manus" / "skills",
        Path.home() / "skills",
        Path.home() / ".cursor" / "skills",
        Path.cwd() / "skills",
    ]:
        if candidate.exists():
            install_dir = candidate / skill["id"]
            break
    
    install_dir.mkdir(parents=True, exist_ok=True)
    target = install_dir / "SKILL.md"
    
    print(f"\n{C.BOLD}Installing {skill['name']}...{C.END}")
    print(f"  Downloading from: {skill['raw_url']}")
    print(f"  Installing to:    {target}")
    
    try:
        urllib.request.urlretrieve(skill["raw_url"], str(target))
        print(f"\n  {C.GREEN}✅ Successfully installed {skill['name']}!{C.END}")
        print(f"  Location: {target}")
        print(f"\n  Your AI agent will automatically detect this skill.")
    except urllib.error.URLError as e:
        print(f"\n  {C.RED}❌ Download failed: {e}{C.END}")
        print(f"  Try manually: curl -o SKILL.md {skill['raw_url']}")
    print()

def cmd_categories(args):
    cats = {}
    for s in CATALOG:
        cats.setdefault(s["category"], []).append(s)
    
    print(f"\n{C.BOLD}SkillFlow Categories{C.END}\n")
    for cat, skills in sorted(cats.items()):
        print(f"  {C.BOLD}{C.CYAN}{cat}{C.END} ({len(skills)} skills)")
        for s in skills:
            print(f"    - {s['name']} {C.DIM}(trust: {s['trust']}){C.END}")
        print()

def cmd_publishers(args):
    pubs = {}
    for s in CATALOG:
        pubs.setdefault(s["publisher"], []).append(s)
    
    print(f"\n{C.BOLD}SkillFlow Publishers{C.END}\n")
    for pub, skills in sorted(pubs.items(), key=lambda x: -len(x[1])):
        avg_trust = sum(s["trust"] for s in skills) // len(skills)
        tc = trust_color(avg_trust)
        print(f"  {C.BOLD}{pub}{C.END} — {len(skills)} skills, avg trust: {tc}{avg_trust}/100{C.END}")
        for s in skills:
            print(f"    {s['name']} {C.DIM}({s['id']}){C.END}")
        print()

def main():
    no_color()
    
    parser = argparse.ArgumentParser(
        prog="skillflow",
        description="SkillFlow CLI — Search, discover, and install AI agent skills",
        epilog="Visit https://skillflow.builders for more skills"
    )
    parser.add_argument("--version", "-v", action="version", version=f"skillflow {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # search
    p_search = subparsers.add_parser("search", help="Search for skills")
    p_search.add_argument("query", nargs="+", help="Search query")
    
    # trending
    subparsers.add_parser("trending", help="Show trending skills")
    
    # info
    p_info = subparsers.add_parser("info", help="Get skill details")
    p_info.add_argument("skill_id", help="Skill ID")
    
    # install
    p_install = subparsers.add_parser("install", help="Install a skill")
    p_install.add_argument("skill_id", help="Skill ID")
    
    # categories
    subparsers.add_parser("categories", help="List categories")
    
    # publishers
    subparsers.add_parser("publishers", help="List publishers")
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    commands = {
        "search": cmd_search,
        "trending": cmd_trending,
        "info": cmd_info,
        "install": cmd_install,
        "categories": cmd_categories,
        "publishers": cmd_publishers,
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()
