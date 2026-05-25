# CSV Export Guide

## 1. Purpose

Create a Linux account CSV from a web address book group.

The generated CSV should contain only the fields required for Linux account provisioning.

## 2. Required CSV Columns

```csv
name,email,account_id,department,position,status,role
User One,user01@example.com,user01,dev,staff,active,user
Admin One,admin01@example.com,admin01,dev,manager,active,admin
```

## 3. Browser Console Export

Open the address book group page, then run the following script in Chrome DevTools Console.

Change `groupId` to the group number in the address book URL.

```javascript
(async () => {
  const groupId = 204;
  const url = `/api/contact/personal/group/${groupId}/contacts?offset=100&page=0&property=nameInitialConsonant&direction=asc`;

  const res = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: { 'Accept': 'application/json' }
  });

  if (!res.ok) {
    throw new Error(`API request failed: ${res.status} ${res.statusText}`);
  }

  const json = await res.json();
  const contacts = json.data || [];

  const reserved = new Set([
    'root', 'admin', 'test', 'oracle', 'mysql', 'postgres', 'nginx', 'apache', 'docker'
  ]);

  const rows = contacts
    .filter(v => v.email)
    .map(v => {
      const email = String(v.email || '').trim().toLowerCase();
      const accountId = email.split('@')[0];
      return {
        name: v.name || '',
        email,
        account_id: accountId,
        department: v.departmentName || '',
        position: v.positionName || '',
        status: 'active',
        role: reserved.has(accountId) ? 'review' : 'user'
      };
    });

  const headers = ['name', 'email', 'account_id', 'department', 'position', 'status', 'role'];
  const escapeCsv = value => `"${String(value ?? '').replaceAll('"', '""')}"`;

  const csv = [
    headers.join(','),
    ...rows.map(row => headers.map(h => escapeCsv(row[h])).join(','))
  ].join('\r\n');

  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  const downloadUrl = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `users_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(downloadUrl);

  console.table(rows);
  console.log(`CSV exported: ${rows.length} rows`);
})();
```

## 4. Notes

- Short account IDs are allowed.
- `account_id` is generated from the email prefix.
- Review rows with `role=review` before applying the CSV.
- Do not commit the generated operational CSV file to Git.
