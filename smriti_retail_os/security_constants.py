# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/security_constants.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/security_constants.py
# @description: Security constants for SMRITI Retail OS backup and config exports.
# @author: Antigravity AI
# @date: 2026-06-10
# @version: 1.8.2a
#

SENSITIVE_EXPORT_FIELDS = [
    "backup_encryption_key",
    "db_password",
    "mail_password",
    "secret_key",
    "encryption_key",
]

PROTECTED_CONFIG_PATTERNS = [
    "*site_config*.json",
    "*secret*",
    "*credential*",
    "*.pem",
    "*.key",
    "*.p12",
    "private/print_jobs/*",
]

GPG_CIPHER_ALGO = "AES256"
ENCRYPTED_BACKUP_SUFFIX = ".smriti.enc"
METADATA_SUFFIX = ".smriti.json"
OTP_EXPIRY_MINUTES = 15

