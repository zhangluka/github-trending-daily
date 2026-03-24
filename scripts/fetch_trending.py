import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_trending_top20():
    url = "https://github.com/trending?since=daily"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    repos = []
    
    for i, article in enumerate(soup.select('article.Box-row'), 1):
        if i > 20:
            break
            
        # 仓库名称和链接
        h2 = article.select_one('h2 a')
        title = h2.text.strip().replace('\n', ' ').replace('  ', ' ')
        link = "https://github.com" + h2['href']
        
        # 描述
        desc_tag = article.select_one('p')
        desc = desc_tag.text.strip() if desc_tag else "No description"
        
        # 语言
        lang_tag = article.select_one('span[itemprop="programmingLanguage"]')
        lang = lang_tag.text.strip() if lang_tag else "Unknown"
        
        # 今日 stars
        stars_tag = article.select_one('span.d-inline-block.float-sm-right')
        stars_today = stars_tag.text.strip() if stars_tag else "N/A"
        
        repos.append(f"""
        <h3>#{i} <a href="{link}">{title}</a></h3>
        <p>{desc}</p>
        <p><strong>语言：</strong>{lang}　　<strong>今日新增：</strong>{stars_today}</p>
        <hr>
        """)
    
    return "".join(repos)

def send_email(content):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"GitHub Trending 前20 - {datetime.now().strftime('%Y-%m-%d')}（北京时间）"
    msg['From'] = os.getenv('SMTP_USER')
    msg['To'] = os.getenv('EMAIL_TO')
    
    html = f"""
    <html>
    <body>
        <h2>GitHub 今日 Trending 前 20 名仓库</h2>
        <p>更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}（北京时间）</p>
        {content}
        <p style="color:#666;">此邮件由 GitHub Actions 自动发送</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        server.send_message(msg)

if __name__ == "__main__":
    trending_html = get_trending_top20()
    send_email(trending_html)
    print("✅ Trending 前20 已发送")
