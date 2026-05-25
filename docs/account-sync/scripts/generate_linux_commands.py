#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shlex
from pathlib import Path


def q(value: str) -> str:
    return shlex.quote(value)


def normalize(value: str | None) -> str:
    return (value or "").strip().strip('"')


def iter_users(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {
                "name": normalize(row.get("name")),
                "email": normalize(row.get("email")).lower(),
                "account_id": normalize(row.get("account_id")).lower(),
                "department": normalize(row.get("department")),
                "position": normalize(row.get("position")),
                "status": normalize(row.get("status")).lower(),
                "role": normalize(row.get("role")).lower(),
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Linux account command plan")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--admin-group", default="wheel")
    parser.add_argument("--user-group", default="account-users")
    args = parser.parse_args()

    print("# Review before execution")
    print(f"groupadd -f {q(args.user_group)}")
    print("")

    for user in iter_users(args.csv_file):
        account_id = user["account_id"]
        if not account_id:
            continue

        status = user["status"]
        role = user["role"]
        gecos = f"{user['name']} <{user['email']}>".strip()

        print(f"# {user['name']} / {user['email']} / {user['department']} / {role} / {status}")
        if status == "active":
            print(f"id {q(account_id)} >/dev/null 2>&1 || useradd -m -s /bin/bash -c {q(gecos)} {q(account_id)}")
            print(f"usermod -aG {q(args.user_group)} {q(account_id)}")
            if role == "admin":
                print(f"usermod -aG {q(args.admin_group)} {q(account_id)}")
        elif status == "inactive":
            print(f"id {q(account_id)} >/dev/null 2>&1 && usermod -L {q(account_id)}")
        print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
