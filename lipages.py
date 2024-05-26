'''
linked pages, very personal blog script. use at YOUR OWN RISK!!!
> python lipages.py add 2023-12-22-新文章.md "新文章标题" --author "作者名" --tags "标签1" --tags "标签2"
> python lipages.py dlt 2023-12-22-新文章.md
> python lipages.py fix 2023-12-22-新文章.md "新的标题"
> python lipages.py lst
'''

import os, re
import click as cli
from datetime import datetime

BLOG_DIR = "blogs"
BLOG_AUTHOR = "lip"
BLOG_INDEX = "README.md"

def ensure_blog_dir():
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)

def create_blog_file(filename, title, author, tags):
    date_pattern = r'\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}|\w{3}\s\d{1,2},?\s\d{4}'
    match = re.search(date_pattern, filename)
    if match: date_strbgn, date_strend = match.span()
    the_date = "" if not match else filename[date_strbgn:date_strend]
    #
    ensure_blog_dir()
    filepath = os.path.join(BLOG_DIR, filename)
    if os.path.exists(filepath): return (f'ERROR {filepath} already exists! Not added!')
    #
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n") # line 0  # 这里不要随意增删条目, 否则后面fix/lst处理文章标题时就会出错
        f.write(f"Title: {title}\n")
        f.write(f"Date: {the_date}\n") # 需要判断...
        f.write(f"Author: {author}\n")
        f.write(f"Tags: [{', '.join(tags)}]\n")
        f.write("---\n")
        f.write("\n") # line 6
        f.write(f"# {title}\n")
        f.write("\n")
        f.write("<!-- Write your content here -->\n")
    return filepath

def update_index(action, filename, title=None):
    with open(BLOG_INDEX, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if action == 'add':
        new_line = f"- [{title}](blogs/{filename})\n"
        lines.append(new_line)
    elif action == 'dlt':
        lines = [line for line in lines if f"blogs/{filename}" not in line]

    with open(BLOG_INDEX, 'w', encoding='utf-8') as f: f.writelines(lines)

@cli.group()
def lipages(): pass

@lipages.command()
@cli.argument('filename')
@cli.argument('title')
@cli.option('--author', default=BLOG_AUTHOR, help='The author of the blog post')
@cli.option('--tags', multiple=True, help='Tags for the blog post')
def add(filename, title, author, tags):
    """Add (initialize) a new blog post."""
    filepath = create_blog_file(filename, title, author, tags)
    if filepath.startswith('ERROR'):
        cli.echo('Not added for the file already exists!')
    else:
        the_path = update_index('add', filename, title)
        cli.echo(f"Created new blog post at {filepath} and updated {BLOG_INDEX}")

@lipages.command()
@cli.argument('filename')
def dlt(filename):
    """Delete a blog post."""
    filepath = os.path.join(BLOG_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        update_index('dlt', filename)
        cli.echo(f"Deleted blog post {filename} and updated {BLOG_INDEX}")
    else:
        cli.echo(f"File {filename} does not exist")

@lipages.command()
@cli.argument('filename')
@cli.argument('new_title')
def fix(filename, new_title):
    """Fix (modify) a blog post title."""
    filepath = os.path.join(BLOG_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            lines[1] = f"Title: {new_title}\n"
            lines[7] = f"# {new_title}\n"  # 注意与文章格式一致(creat函数)
            f.seek(0)
            f.writelines(lines)

        update_index('dlt', filename)
        update_index('add', filename, new_title)
        cli.echo(f"Modified blog post {filename} title to {new_title} and updated {BLOG_INDEX}")
    else:
        cli.echo(f"File {filename} does not exist")

@lipages.command()
def lst():
    """List all blog posts."""
    ensure_blog_dir()
    files = os.listdir(BLOG_DIR)
    if not files:
        cli.echo("No blog posts found.")
        return

    for filename in files:
        filepath = os.path.join(BLOG_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f: lines = f.readlines()
        title = '' if len(lines)<=1 else lines[1].strip('Title:').strip()  # 注意与文章格式一致!!
        cli.echo(f"{filename} - {title}")

if __name__ == "__main__": lipages()
