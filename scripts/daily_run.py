#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定时运行脚本 - 自动检索并发送报告
可用于 crontab 或 Windows 计划任务
"""

import os
import sys
import subprocess

# ========== 配置区域 - 请根据需要修改 ==========

CONFIG = {
    # 要检索的宿主物种 (可选: "cattle", "sheep", "goat", "yak", "buffalo", "all")
    "hosts": ["cattle", "sheep"],

    # 输出目录
    "output_dir": os.path.expanduser("~/Desktop/瘤胃宏基因组报告"),

    # 收件人邮箱地址
    "email_to": "your_email@example.com",
}

# ==============================================


def main():
    print("=" * 50)
    print("瘤胃宏基因组数据集自动检索任务")
    print("=" * 50)

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    collector_script = os.path.join(script_dir, "rumen_collector.py")
    sender_script = os.path.join(script_dir, "send_report.py")

    # 检查是否设置了邮箱配置
    smtp_user = os.environ.get("RUMEN_SMTP_USER")
    smtp_pass = os.environ.get("RUMEN_SMTP_PASS")

    if not smtp_user or not smtp_pass:
        print("\n[警告] 未设置邮箱环境变量，将跳过邮件发送")
        print("如需发送邮件，请先设置:")
        print("  export RUMEN_SMTP_USER='your_email@example.com'")
        print("  export RUMEN_SMTP_PASS='your_auth_code'")
        print()

    # 遍历每个宿主物种
    for host in CONFIG["hosts"]:
        print(f"\n{'='*50}")
        print(f"开始检索: {host}")
        print(f"{'='*50}")

        # 运行数据集检索
        cmd = [
            sys.executable,
            collector_script,
            "--host", host,
            "--output", CONFIG["output_dir"],
            "--max-results", "200"
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            # 打印输出
            print(result.stdout)

            # 如果有错误，打印错误信息
            if result.stderr:
                print("[错误信息]", result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"[错误] 检索 {host} 失败: {e}")
            continue
        except Exception as e:
            print(f"[错误] 发生异常: {e}")
            continue

        # 查找生成的报告文件
        output_files = []
        if os.path.exists(CONFIG["output_dir"]):
            for filename in os.listdir(CONFIG["output_dir"]):
                if filename.startswith(f"{host}_rumen_metagenome_report_") and filename.endswith(".html"):
                    output_files.append(os.path.join(CONFIG["output_dir"], filename))

        # 找到最新的报告
        if output_files:
            output_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            latest_report = output_files[0]

            print(f"\n最新报告: {latest_report}")

            # 发送邮件
            if smtp_user and smtp_pass:
                print("\n发送邮件...")
                email_cmd = [
                    sys.executable,
                    sender_script,
                    latest_report,
                    CONFIG["email_to"]
                ]

                try:
                    email_result = subprocess.run(
                        email_cmd,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                    print(email_result.stdout)

                    if email_result.stderr:
                        print("[邮件错误]", email_result.stderr)

                    if email_result.returncode == 0:
                        print("邮件发送成功！")
                    else:
                        print("邮件发送失败")

                except Exception as e:
                    print(f"[错误] 发送邮件时发生异常: {e}")
            else:
                print("\n[跳过] 未配置邮箱，跳过邮件发送")
        else:
            print(f"[警告] 未找到 {host} 的报告文件")

    print("\n" + "=" * 50)
    print("所有任务完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
