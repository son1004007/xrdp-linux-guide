#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["name", "email", "account_id", "department", "position", "status", "role"]
VALID_STATUS = {"active", "inactive"}
VALID_ROLE = {"user", "admin", "review"}
RESERVED_USERS = {"root", "admin", "test", "oracle", "mysql", "postgres", "nginx", "apache", "docker"}
ACCOUNT_ID_RE = re.compile(r"^[a-z_][a-z0-9_-]*[$]?")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize(value: str | None) -> str:
    return (value or "").strip().strip('"')


def validate_csv(path: Path) -> int:
    errors: list[str] = []
    seen_accounts: set[str] = set()
    seen_emails: set[str] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            errors.append(f"missing columns: {', '.join(missing)}")
            return print_errors(errors)

        for line_no, row in enumerate(reader, start=2):
            name = normalize(row.get("name"))
            email = normalize(row.get("email")).lower()
            account_id = normalize(row.get("account_id")).lower()
            status = normalize(row.get("status")).lower()
            role = normalize(row.get("role")).lower()

            if not name:
                errors.append(f"line {line_no}: empty name")
            if not email or not EMAIL_RE.match(email):
                errors.append(f"line {line_no}: invalid email: {email}")
            if not account_id or not ACCOUNT_ID_RE.fullmatch(account_id):
                errors.append(f"line {line_no}: invalid account_id: {account_id}")
            elif account_id in RESERVED_USERS:
                errors.append(f"line {line_no}: reserved account_id: {account_id}")
            if status not in VALID_STATUS:
                errors.append(f"line {line_no}: invalid status: {status}")
            if role not in VALID_ROLE:
                errors.append(f"line {line_no}: invalid role: {role}")
            if account_id in seen_accounts:
                errors.append(f"line {line_no}: duplicated account_id: {account_id}")
            if email in seen_emails:
                errors.append(f"line {line_no}: duplicated email: {email}")
            seen_accounts.add(account_id)
            seen_emails.add(email)

    if errors:
        return print_errors(errors)

    print(f"OK: {path} is valid. users={len(seen_accounts)}")
    return 0


def print_errors(errors: list[str]) -> int:
    for error in errors:
        print(error, file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    return validate_csv(args.csv_file)


if __name__ == "__main__":
    raise SystemExit(main())
