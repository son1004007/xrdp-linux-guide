# Linux User Sync Procedure

## 1. Purpose

Apply a user CSV to a Linux server.

The script creates missing active accounts, assigns groups, and locks inactive accounts.

## 2. Files

```text
account-sync/
├── sample-users.csv
└── sync-linux-users.sh
```

Operational CSV files should be stored on the target server, not in Git.

Recommended path:

```text
/opt/account-sync/users.csv
```

## 3. CSV Format

```csv
name,email,account_id,department,position,status,role
User One,user01@example.com,user01,dev,staff,active,user
Admin One,admin01@example.com,admin01,dev,manager,active,admin
```

## 4. Prepare Server

```bash
sudo mkdir -p /opt/account-sync
sudo cp users.csv /opt/account-sync/users.csv
sudo cp sync-linux-users.sh /opt/account-sync/sync-linux-users.sh
sudo chmod 600 /opt/account-sync/users.csv
sudo chmod 700 /opt/account-sync/sync-linux-users.sh
```

## 5. Dry Run

Always run dry-run first.

```bash
cd /opt/account-sync
sudo ./sync-linux-users.sh users.csv dry-run
```

Review the printed commands before applying changes.

## 6. Apply

```bash
cd /opt/account-sync
sudo ./sync-linux-users.sh users.csv apply
```

## 7. Verify

Check account existence:

```bash
id user01
```

Check groups:

```bash
groups user01
```

Check admin group:

```bash
getent group wheel
getent group sudo
```

Check locked account status:

```bash
passwd -S old01
```

## 8. Role Mapping

| role | Action |
|---|---|
| user | Add to `account-users` group |
| admin | Add to `account-users` and admin group |

Admin group is selected automatically.

- Red Hat compatible systems: `wheel`
- Debian compatible systems: `sudo`

## 9. Status Mapping

| status | Action |
|---|---|
| active | Create account if missing and assign groups |
| inactive | Lock account if it exists |

The script does not delete accounts.

## 10. Notes

- Short account IDs are allowed.
- The CSV parser is simple and assumes comma-separated fields without embedded commas.
- If a field can contain commas, clean the CSV before applying it.
- Apply to a test server before applying to production servers.
