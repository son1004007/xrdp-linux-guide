# 중앙 계정 관리 운영 기준

## 1. 운영 원칙

중앙 계정 관리는 다음 원칙을 기준으로 운영합니다.

- 계정 원본은 중앙 CSV 파일로 관리
- 서버별 수동 계정 생성 최소화
- 신규 계정은 active 상태일 때만 생성
- 퇴사자 또는 제외 대상자는 inactive 상태로 잠금 처리
- 계정 삭제는 자동화하지 않음
- 관리자 권한은 최소 인원에게만 부여
- 모든 변경 내역은 로그로 남김

---

## 2. 계정 관리 프로세스

## 2.1 신규 사용자 추가

1. 근무자 정보 확인
2. CSV 파일에 사용자 추가
3. status 값을 active로 설정
4. role 값을 user 또는 admin으로 설정
5. 검증 스크립트 실행
6. 동기화 스크립트 실행
7. 대상 서버 로그인 확인

예:

```csv
name,email,department,status,role
홍길동,hong@example.com,빅데이터사업부,active,user
```

---

## 2.2 사용자 비활성화

퇴사자, 전출자, 프로젝트 제외자는 계정을 삭제하지 않고 잠금 처리합니다.

1. CSV 파일에서 status 값을 inactive로 변경
2. 동기화 스크립트 실행
3. 로그인 차단 여부 확인
4. 홈 디렉터리와 소유 파일 이관 여부 검토

예:

```csv
name,email,department,status,role
홍길동,hong@example.com,빅데이터사업부,inactive,user
```

Linux 계정 잠금 명령 예시는 다음과 같습니다.

```bash
sudo passwd -l hong
sudo usermod -L hong
```

---

## 2.3 관리자 권한 부여

관리자 권한은 role 값을 admin으로 지정한 사용자에게만 부여합니다.

Red Hat 계열:

```bash
sudo usermod -aG wheel username
```

Debian 계열:

```bash
sudo usermod -aG sudo username
```

관리자 권한은 정기적으로 점검합니다.

```bash
getent group wheel
getent group sudo
```

---

## 3. 파일 권한 기준

중앙 서버의 사용자 정보 파일은 root 또는 지정 관리자만 수정할 수 있어야 합니다.

```bash
sudo chown root:root /opt/account-sync/data/users.csv
sudo chmod 640 /opt/account-sync/data/users.csv
```

스크립트 파일은 실행 권한을 제한합니다.

```bash
sudo chown root:root /opt/account-sync/scripts/*.sh
sudo chmod 750 /opt/account-sync/scripts/*.sh
```

---

## 4. 로그 관리

동기화 작업은 다음 항목을 로그로 남깁니다.

- 실행 시간
- 대상 서버
- 생성 계정
- 변경 계정
- 비활성화 계정
- 관리자 권한 부여 내역
- 오류 내용

로그 파일 예시는 다음과 같습니다.

```text
/opt/account-sync/logs/sync.log
```

권장 로그 형식:

```text
2026-05-25 10:00:00 CREATE user=hong server=rocky-dev-01 result=success
2026-05-25 10:01:00 LOCK user=leave server=ubuntu-dev-01 result=success
```

---

## 5. 보안 기준

## 5.1 root 계정 관리

- root 원격 로그인은 비활성화 권장
- 장애 대응용 로컬 관리자 계정은 최소 1개 유지
- 중앙 인증 장애 시 복구 가능한 계정을 확보

SSH 설정 예시:

```text
PermitRootLogin no
PasswordAuthentication no
```

---

## 5.2 비밀번호 정책

CSV 기반 로컬 계정 동기화 단계에서는 비밀번호 정책 통합이 제한됩니다.

권장 방식은 다음과 같습니다.

- 초기 비밀번호 수동 전달 금지
- SSH Key 기반 접속 우선
- 비밀번호 로그인 최소화
- FreeIPA 전환 시 중앙 비밀번호 정책 적용

---

## 5.3 SSH Key 관리

가능하면 사용자별 SSH 공개키를 별도 컬럼 또는 별도 파일로 관리합니다.

예:

```text
/opt/account-sync/data/ssh-keys/hong.pub
```

동기화 시 다음 경로에 배포합니다.

```text
/home/hong/.ssh/authorized_keys
```

권한은 다음과 같이 설정합니다.

```bash
chmod 700 /home/hong/.ssh
chmod 600 /home/hong/.ssh/authorized_keys
chown -R hong:hong /home/hong/.ssh
```

---

## 6. 운영 점검 명령어

## 6.1 사용자 확인

```bash
getent passwd username
id username
```

## 6.2 그룹 확인

```bash
groups username
getent group wheel
getent group sudo
```

## 6.3 계정 잠금 확인

```bash
sudo passwd -S username
sudo chage -l username
```

## 6.4 최근 로그인 확인

```bash
last username
lastlog -u username
```

---

## 7. 장애 대응

## 7.1 신규 계정 생성 실패

확인 항목:

- CSV 파일 형식 오류
- 계정명 중복
- 금지 계정명 사용
- sudo 권한 부족
- 홈 디렉터리 생성 실패

## 7.2 XRDP 로그인 실패

확인 항목:

- Linux 계정 생성 여부
- 계정 잠금 여부
- 홈 디렉터리 권한
- `.Xclients` 또는 `.xsession` 파일 존재 여부
- XRDP 서비스 상태

명령어:

```bash
sudo systemctl status xrdp
sudo tail -f /var/log/xrdp.log
sudo tail -f /var/log/xrdp-sesman.log
```

## 7.3 SSH 로그인 실패

확인 항목:

- 계정 잠금 여부
- SSH 공개키 배포 여부
- `.ssh` 디렉터리 권한
- sshd 설정

명령어:

```bash
sudo tail -f /var/log/secure
sudo tail -f /var/log/auth.log
```

---

## 8. 정기 점검 항목

| 주기 | 점검 항목 |
|---|---|
| 매주 | 신규/비활성 계정 반영 여부 |
| 매주 | 관리자 그룹 구성원 확인 |
| 매월 | 미사용 계정 확인 |
| 매월 | SSH Key 현황 확인 |
| 분기 | 계정 동기화 로그 보관 상태 확인 |
| 분기 | FreeIPA 또는 Samba AD 전환 필요성 검토 |

---

## 9. 운영 시 주의사항

- 계정 삭제 자동화는 금지합니다.
- inactive 사용자는 잠금 처리 후 홈 디렉터리 보존을 기본값으로 둡니다.
- 관리자 권한은 role=admin인 사용자에게만 부여합니다.
- CSV 파일 수정자는 최소화합니다.
- 동기화 스크립트 실행 전 CSV 검증을 먼저 수행합니다.
- 운영 서버 일괄 적용 전 테스트 서버에서 먼저 검증합니다.

---

## 10. 결론

중앙 계정 관리는 계정 생성 자동화보다 계정 비활성화와 권한 회수의 안정성이 더 중요합니다.

초기 운영에서는 삭제보다 잠금, 자동화보다 검증, 편의성보다 감사 가능성을 우선합니다.
