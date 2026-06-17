# -*- coding: utf-8 -*-
#
# @file: test_db.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import json, pymysql

with open('sites/common_site_config.json') as f:
    common = json.load(f)
with open('sites/smriti_retail/site_config.json') as f:
    site = json.load(f)

conn = pymysql.connect(
    host=common.get('db_host') or 'db',
    port=common.get('db_port') or 3306,
    user=site['db_name'],
    password=site['db_password'],
    database=site['db_name'],
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute('SELECT name, title FROM `tabPage` WHERE name LIKE %s', ('%report%',))
    for row in cur.fetchall():
        print(row)
