#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
发送报告邮件 - 支持Python 2/3
用法:
    python send_report.py 报告.html 收件人@example.com
"""

from __future__ import print_function
import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header

def send_email(report_path, recipient):
    """
    发送报告邮件

    参数:
        report_path: 报告文件路径
        recipient: 收件人邮箱地址
    """
    # 从环境变量读取配置
    smtp_user = os.environ.get("RUMEN_SMTP_USER")
    smtp_pass = os.environ.get("RUMEN_SMTP_PASS")

    if not smtp_user or not smtp_pass:
        print("[错误] 未设置邮箱配置")
        print("请先设置环境变量:")
        print("  export RUMEN_SMTP_USER='your_email@example.com'")
        print("  export RUMEN_SMTP_PASS='your_auth_code'")
        print("\n注意:")
        print("  - SMTP_USER: 发送邮箱地址")
        print("  - SMTP_PASS: 邮箱授权码(不是登录密码)")
        return False

    # 检查报告文件是否存在
    if not os.path.exists(report_path):
        print("[错误] 报告文件不存在:", report_path)
        return False

    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient
        msg['Subject'] = Header(u'瘤胃宏基因组数据集检索报告', 'utf-8')

        # 邮件正文
        body = u"""
您好！

这是最新的瘤胃宏基因组数据集检索报告。

报告包含:
- ENA 数据库结果
- NCBI SRA 数据库结果
- NCBI Genome 数据库结果
- 数据集详细信息和下载链接

如有问题，请查看附件中的完整报告。

此邮件由 Rumen Metagenome Collector 自动发送。
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # 添加附件
        filename = os.path.basename(report_path)
        with open(report_path, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment',
                           filename=Header(filename, 'utf-8').encode())
            msg.attach(part)

        # 发送邮件
        print("连接到邮件服务器...")
        # 根据邮箱类型选择SMTP服务器
        if smtp_user.endswith('@qq.com'):
            smtp_server = 'smtp.qq.com'
            smtp_port = 587
        elif smtp_user.endswith('@163.com'):
            smtp_server = 'smtp.163.com'
            smtp_port = 465
        elif smtp_user.endswith('@gmail.com'):
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
        elif smtp_user.endswith('@outlook.com'):
            smtp_server = 'smtp.office365.com'
            smtp_port = 587
        else:
            # 默认配置（适用于大多数邮箱）
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            print(f"[提示] 使用默认SMTP服务器: {smtp_server}")

        print(f"SMTP服务器: {smtp_server}:{smtp_port}")

        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls()
            print("登录邮箱...")
            server.login(smtp_user, smtp_pass)
            print("发送邮件...")
            server.send_message(msg)
            print("发送成功！")

        return True

    except smtplib.SMTPAuthenticationError:
        print("[错误] 邮箱认证失败")
        print("请检查:")
        print("  1. SMTP_USER 是否正确")
        print("  2. SMTP_PASS 是否是授权码(不是登录密码)")
        print("\n如何获取授权码:")
        print("  - QQ邮箱: 设置 -> 账户 -> 开启SMTP -> 生成授权码")
        print("  - 163邮箱: 设置 -> POP3/SMTP/IMAP -> 开启SMTP -> 获取授权码")
        print("  - Gmail: 账户安全 -> 两步验证 -> 应用专用密码")
        return False

    except smtplib.SMTPException as e:
        print("[错误] SMTP错误:", str(e))
        return False

    except Exception as e:
        print("[错误] 发送失败:", str(e))
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python send_report.py 报告.html 收件人@example.com")
        sys.exit(1)

    report_file = sys.argv[1]
    recipient_email = sys.argv[2]

    success = send_email(report_file, recipient_email)
    sys.exit(0 if success else 1)
