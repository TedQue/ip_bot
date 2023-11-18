#!/usr/bin/env python3
import sys
import re
import argparse
import smtplib
import random

# 第三方库
import requests

# 本地源码包
import jjson

APP_NAME = "IP Bot"
VERSION = "0.1.3"
AUTHOR = "Que's C++ Studio"

CONF_KEY_TEST = "test"
CONF_KEY_SHUFFLE = "shuffle"
CONF_KEY_URLS = "urls"
CONF_KEY_SAVE_LAST_IP = "save_last_ip"

CONF_KEY_SMTP_SSL = "smtp_ssl"
CONF_KEY_SMTP_HOST = "smtp_host"
CONF_KEY_SMTP_PORT = "smtp_port"
CONF_KEY_SMTP_USERNAME = "smtp_username"
CONF_KEY_SMTP_PWD = "smtp_password"
CONF_KEY_SMTP_MAIL_FROM = "smtp_mail_from"
CONF_KEY_SMTP_MAIL_TO = "smtp_mail_to"
CONF_KEY_SMTP_MAIL_SUBJECT = "smtp_mail_subject"
CONF_KEY_SMTP_MAIL_CONTENT = "smpt_mail_content"

TOKEN_IP = "%IP%"
PAT_IP = r"((\d{1,3}\.){3}\d{1,3})"

def load_conf(fn):
	try:
		return jjson.load(fn)
	except Exception as e:
		print(f"failed to load configure file: {e}")
		return None

def brief(s, max_len):
	return s if len(s) <= max_len else s[: max_len // 2] + ' .. ' + s[-max_len // 2:]

def get_ip_address(conf, test):
	headers = {
		"User-Agent":
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
			" Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
	}
	urls = conf.get(CONF_KEY_URLS, [])

	# 打乱 url 列表,避免每次都从同一个数据源开始
	if conf.get(CONF_KEY_SHUFFLE, True):
		random.seed()
		urls = random.sample(urls, k=len(urls))

	# 依次访问指定网页尝试获取 IP 地址
	# 如果是测试模式,则会尝试所有配置选项,非测试模式则在第一个成功尝试后立即返回
	for i in urls:
		# url 选项必须至少包含页面地址和正则串两项
		assert isinstance(i, list) and len(i) >= 2
		url, pat = i[0], i[1]
		pat = pat.replace(TOKEN_IP, PAT_IP)

		# 如果 url 选项包含第 3 项,并且该项类型是 int,则为正则捕获组索引,不指定的话默认索引为 1
		group_idx = i[2] if len(i) >= 3 and isinstance(i[2], int) else 1

		print(f"attempt to get IP address from \"{url}\" with pattern \"{pat}\" ...")
		response = requests.get(url, headers=headers, timeout=60)
		if response and response.status_code == 200:
			m = re.search(pat, response.text, re.I | re.S)
			if m:
				if group_idx in range(len(m.groups()) + 1):
					print(f"success: \"{m[group_idx]}\"")
					if not test:
						return m[group_idx]
				else:
					print(f"failed: invalid regex group index [{group_idx}] of {m.groups()}")
			else:
				print(f"failed: pattern \"{pat}\" not found in \"{brief(response.text, 200)}\"")
		else:
			st = response.status_code if response else 0
			print(f"failed: response code {st}")
	return None

def send_mail(conf, ip):
	svr = smtplib.SMTP_SSL(None) if conf.get(CONF_KEY_SMTP_SSL, True) else smtplib.SMTP(None)

	# 连接服务器
	host = conf.get(CONF_KEY_SMTP_HOST, "")
	port = conf.get(CONF_KEY_SMTP_PORT, 25)
	assert host, f"host name can't be empty"

	try:
		print(f"connecting to stmp server {host}:{port} ... ", end='')
		r = svr.connect(host, port)
		print(r)
	except Exception as e:
		print(f"failed {e}")
		return False

	# 登录
	username = conf.get(CONF_KEY_SMTP_USERNAME, "")
	password = conf.get(CONF_KEY_SMTP_PWD, "")
	assert username, f"username can't be empty"
	assert password, f"password can't be empty"

	try:
		print(f"login {username} ... ", end='')
		r = svr.login(username, password)
		print(r)
	except Exception as e:
		print(f"failed {e}")
		return False

	# 发送邮件
	mail_from = conf.get(CONF_KEY_SMTP_MAIL_FROM, "")
	mail_to = conf.get(CONF_KEY_SMTP_MAIL_TO, "")
	assert mail_from, f"mail from address can't be empty"
	assert mail_to, f"mail to address can't be empty"
	mail_subject = conf.get(
		CONF_KEY_SMTP_MAIL_SUBJECT,
		f"Your IP Address: {TOKEN_IP}"
	).replace(TOKEN_IP, ip)
	mail_content = conf.get(
		CONF_KEY_SMTP_MAIL_CONTENT,
		f"Hello,\r\nYour IP address is: {TOKEN_IP}\r\n\r\n{APP_NAME} v{VERSION} by {AUTHOR}"
	).replace(TOKEN_IP, ip)
	msg = f"From: {mail_from}\r\nTo: {mail_to}\r\nSubject: {mail_subject}\r\n\r\n{mail_content}"

	try:
		print(f"sending mail from \"{mail_from}\" to \"{mail_to}\" ... ", end='')
		r = svr.sendmail(mail_from, mail_to, msg)
		print(r)
	except Exception as e:
		print(f"failed {e}")
		return False

	# 登出
	print(f"logout ... ", end='')
	r = svr.quit()
	print(r)
	return True

def get_last_ip(conf):
	# 从本地文件中读取上次获取到的 ip 地址,如果该项配置为空,则返回空字符串
	fn = conf.get(CONF_KEY_SAVE_LAST_IP, "")
	if fn:
		try:
			with open(fn, "r", encoding="utf-8") as fp:
				return fp.read()
		except Exception:
			pass
	return ""

def save_last_ip(conf, ip):
	fn = conf.get(CONF_KEY_SAVE_LAST_IP, "")
	if fn:
		try:
			with open(fn, "w", encoding="utf-8") as fp:
				fp.write(ip)
			print(f"IP address \"{ip}\" saved to \"{fn}\"")
		except Exception as e:
			print(f"save IP address failed: {e}")

def main():
	arg_parser = argparse.ArgumentParser(
		prog='ip_bot',
		description='Get IP address from web page and send it as mail',
		epilog=f'{APP_NAME} v{VERSION} (c) {AUTHOR}'
	)
	arg_parser.add_argument("-t", "--test", action="store_true", help="test all optional urls")
	arg_parser.add_argument("--version", action="version", version=f'{APP_NAME} v{VERSION}')
	arg_parser.add_argument("configure", nargs='?', help="configure files", default="default.conf")
	args = arg_parser.parse_args()

	print(f"Welcome to {APP_NAME} v{VERSION} by {AUTHOR}")

	conf = load_conf(args.configure)
	if conf:
		if args.test:
			print(f"testing \"{args.configure}\" ...")
			get_ip_address(conf, True)
		else:
			ip = get_ip_address(conf, False)
			if ip is None:
				print("failed to get IP address")
			else:
				last_ip = get_last_ip(conf)
				if last_ip != ip:
					print(f"IP address changed: from \"{last_ip}\" to \"{ip}\"")
					if send_mail(conf, ip):
						save_last_ip(conf, ip)
				else:
					print(f"IP address remains unchanged: \"{ip}\"")

	print(f"Bye")


# entrance
if __name__ == "__main__":
	main()
