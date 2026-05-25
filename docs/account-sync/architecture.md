# 중앙 계정 동기화 아키텍처

## 1. 문제점

서버별로 사용자 계정을 개별 생성하면 다음 문제가 발생합니다.

- 서버마다 계정명이 달라질 수 있음
- 퇴사자 계정이 일부 서버에 남을 수 있음
- sudo 권한 관리가 분산됨
- XRDP, SSH, 파일 전송 권한을 서버별로 따로 관리해야 함
- 감사 또는 보안 점검 시 계정 현황 파악이 어려움

따라서 계정 원본을 1곳에서 관리하고, 각 서버는 중앙 데이터를 기준으로 동기화하는 구조가 필요합니다.

---

## 2. 전제 조건

다우오피스 직접 연동은 제외합니다.

이유는 다음과 같습니다.

- 그룹웨어 관리자 권한이 없음
- 사용자 API, LDAP, SAML, SCIM 연동 권한을 확보하기 어려움
- 초기 구축 목적은 그룹웨어 통합이 아니라 서버 계정 통제임

따라서 사용자 원본 데이터는 CSV 파일로 관리합니다.

---

## 3. 기준 데이터

CSV 파일은 다음 컬럼을 기준으로 작성합니다.

```csv
name,email,department,status,role
홍길동,hong@example.com,빅데이터사업부,active,user
김관리,admin@example.com,빅데이터사업부,active,admin
이퇴사,leave@example.com,빅데이터사업부,inactive,user
```

| 컬럼 | 설명 | 예시 |
|---|---|---|
| name | 사용자 이름 | 홍길동 |
| email | 업무 이메일 | hong@example.com |
| department | 부서 | 빅데이터사업부 |
| status | 계정 상태 | active / inactive |
| role | 권한 구분 | user / admin |

계정 ID는 이메일 앞부분을 기준으로 생성합니다.

예:

```text
hong@example.com → hong
```

---

## 4. 권장 아키텍처

```text
사용자 CSV 파일
      ↓
중앙 계정 관리 서버
      ↓
계정 검증 및 표준화
      ↓
동기화 스크립트 실행
      ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Red Hat 계열     │ Debian 계열      │ Windows 11       │
│ Rocky/RHEL       │ Ubuntu/Debian    │ 업무 PC/서버      │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## 5. 구성 선택지

## 선택지 A. CSV + OS 로컬 계정 동기화

가장 단순한 방식입니다.

### 구성

- 중앙 서버에 CSV 저장
- 각 서버에서 CSV 다운로드
- Linux는 `useradd`, `usermod`, `passwd -l` 사용
- Windows는 PowerShell `New-LocalUser`, `Disable-LocalUser` 사용

### 장점

- 빠르게 구축 가능
- LDAP/AD 지식이 없어도 운영 가능
- 기존 서버 구조 변경이 작음

### 단점

- 서버별 로컬 계정이므로 완전한 중앙 인증은 아님
- 비밀번호 정책 통합이 제한적
- Windows 연동 자동화는 별도 스크립트 필요

### 적합한 경우

- 초기 MVP
- 서버 수가 적음
- 빠르게 계정 생성/비활성화 자동화가 필요함

---

## 선택지 B. FreeIPA 기반 Linux 중앙 인증

Linux 서버 중심의 권장안입니다.

### 구성

- 중앙 서버에 FreeIPA 설치
- Linux 서버를 FreeIPA Client로 등록
- 사용자, 그룹, SSH Key, sudo 정책을 중앙 관리
- Debian 계열은 SSSD 기반으로 연동

### 장점

- Linux 계정 중앙 관리에 적합
- SSH Key와 sudo 정책 관리 가능
- 계정 비활성화가 즉시 반영됨
- Red Hat 계열 Linux와 궁합이 좋음

### 단점

- FreeIPA 운영 지식 필요
- DNS, Kerberos, 시간 동기화 설정 필요
- Windows 11 직접 연동은 별도 검토 필요

### 적합한 경우

- Linux 서버가 여러 대임
- SSH/XRDP 접속 계정을 통합하려는 경우
- 운영 서버 계정 감사가 필요한 경우

---

## 선택지 C. Samba AD 기반 Windows 포함 중앙 인증

Windows 11까지 포함하려는 경우 검토합니다.

### 구성

- Samba AD Domain Controller 구축
- Windows 11 도메인 조인
- Linux는 SSSD로 AD 연동

### 장점

- Windows 11 도메인 로그인 가능
- Linux와 Windows 계정 체계 통합 가능
- 조직 단위 사용자 관리에 적합

### 단점

- 운영 난이도 높음
- DNS/Kerberos/도메인 정책 이해 필요
- 초기 구축 범위가 커짐

### 적합한 경우

- Windows 11까지 동일 계정으로 로그인해야 함
- 내부 업무망에서 AD 구조가 필요한 경우

---

## 6. 권장 도입 순서

| 단계 | 방식 | 목적 |
|---|---|---|
| 1 | CSV + 로컬 계정 동기화 | 빠른 자동화 |
| 2 | FreeIPA | Linux 중앙 인증 |
| 3 | Samba AD | Windows 11 통합 |

처음부터 FreeIPA와 Samba AD를 동시에 구축하지 않습니다.

우선 Linux 계정 생성과 비활성화 자동화를 성공시킨 뒤, 운영 필요성에 따라 중앙 인증 구조로 확장합니다.

---

## 7. 최종 권장안

현재 환경에서는 다음 구성이 가장 현실적입니다.

```text
1차 목표: CSV 기반 Linux 계정 동기화
2차 목표: FreeIPA 기반 Linux 중앙 인증
3차 목표: Windows 11은 Samba AD로 별도 확장
```

다우오피스 직접 연동 없이도 계정 생성, 권한 부여, 퇴사자 비활성화, 감사 대응 수준은 충분히 개선할 수 있습니다.
