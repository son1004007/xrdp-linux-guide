# Linux XRDP 원격 접속 및 검은 화면 문제 해결 가이드

## 1. 목적

Windows 원격 데스크톱(mstsc)을 이용해 Linux GUI 환경에 XRDP로 접속할 때 필요한 설정과 문제 해결 절차를 정리합니다.

주요 대상은 다음과 같습니다.

- Windows에서 Linux GUI 원격 접속
- XRDP 클립보드 공유
- XRDP 파일 전송
- XRDP 검은 화면 문제 해결
- Rocky Linux / Ubuntu 서버 GUI 운영

---

## 2. 권장 구성

| 항목 | 권장 구성 |
|---|---|
| 원격 접속 | XRDP |
| Linux GUI | XFCE |
| Display Server | X11 |
| 파일 전송 | WinSCP 또는 XRDP Drive Redirection |
| 개발 작업 | VSCode Remote SSH |
| 서버 운영 | GNOME/Wayland 최소화 |

서버형 Linux에서는 GNOME보다 XFCE가 XRDP와 더 안정적으로 동작합니다.

---

## 3. XRDP 기본 설치

### Ubuntu

```bash
sudo apt update
sudo apt install xrdp xorgxrdp -y
sudo systemctl enable --now xrdp
```

### Rocky Linux

```bash
sudo dnf install epel-release -y
sudo dnf install xrdp xorgxrdp -y
sudo systemctl enable --now xrdp
```

---

## 4. Wayland 비활성화

GNOME 환경에서는 Wayland 때문에 XRDP 접속 시 검은 화면이 발생할 수 있습니다.

```bash
sudo vi /etc/gdm/custom.conf
```

아래 설정을 적용합니다.

```ini
WaylandEnable=false
```

적용 후 재부팅합니다.

```bash
sudo reboot
```

---

## 5. XFCE 설치 및 XRDP 세션 지정

### Ubuntu

```bash
sudo apt install xfce4 xfce4-goodies -y
echo "startxfce4" > ~/.xsession
sudo systemctl restart xrdp
```

### Rocky Linux

```bash
sudo dnf groupinstall "Xfce" -y
echo "startxfce4" > ~/.Xclients
chmod +x ~/.Xclients
sudo systemctl restart xrdp
```

Rocky Linux에서는 `~/.Xclients` 파일에 `startxfce4`를 지정하는 방식이 안정적입니다.

---

## 6. 클립보드 공유 설정

Windows에서 `mstsc` 실행 후 다음 항목을 확인합니다.

1. 원격 데스크톱 연결 실행
2. 옵션 표시 선택
3. 로컬 리소스 탭 선택
4. 클립보드 체크

Linux 접속 후 복사/붙여넣기가 되는지 확인합니다.

```bash
ps -ef | grep xrdp-chansrv
```

`xrdp-chansrv` 프로세스가 있어야 클립보드와 드라이브 공유가 정상 동작합니다.

---

## 7. 파일 전송 방법

### 방법 1. XRDP 드라이브 공유

Windows 원격 데스크톱 설정에서 다음을 체크합니다.

```text
로컬 리소스 > 자세히 > 드라이브
```

Linux 접속 후 다음 경로를 확인합니다.

```bash
ls ~/thinclient_drives
```

예시:

```bash
cd ~/thinclient_drives/C/Users/사용자명/Downloads
```

소형 파일 이동에는 적합합니다.

### 방법 2. WinSCP 사용

대용량 파일이나 반복 전송은 WinSCP가 더 안정적입니다.

필요 조건:

- Linux 서버 SSH 접속 가능
- Windows에 WinSCP 설치
- SFTP 방식 사용

접속 예시:

```text
Host: 192.168.x.x
Protocol: SFTP
Port: 22
User: Linux 계정
```

---

## 8. 검은 화면 문제 원인

XRDP 접속 후 검은 화면만 표시되는 경우 주요 원인은 다음과 같습니다.

| 우선순위 | 원인 | 설명 |
|---|---|---|
| 1 | Wayland 사용 | GNOME + Wayland 조합에서 자주 발생 |
| 2 | GUI 세션 미지정 | XRDP가 실행할 Desktop Environment를 찾지 못함 |
| 3 | xorgxrdp 미설치 | Xorg 기반 세션 실행 불가 |
| 4 | 기존 로컬 세션 충돌 | 같은 사용자로 로컬 GUI 로그인 중일 때 발생 |
| 5 | 권한 문제 | `.Xauthority`, `.Xclients` 권한 문제 |

---

## 9. 로그 확인

### XRDP 로그

```bash
sudo tail -f /var/log/xrdp.log
```

### XRDP 세션 로그

```bash
sudo tail -f /var/log/xrdp-sesman.log
```

---

## 10. 로그 예시와 해석

예시 로그:

```text
Starting X server on display 13: Xvnc :13
X server :13 is working
Starting window manager for display :13
Using the default window manager on display 13: /usr/libexec/xrdp/startwm-bash.sh
Session in progress on display :13
```

이 경우 XRDP와 X 서버는 정상적으로 실행된 상태입니다.

문제는 다음 영역일 가능성이 높습니다.

- window manager 실행 실패
- Desktop Environment 미설정
- GNOME/Wayland 충돌
- 사용자 세션 설정 누락

특히 다음 메시지가 보이면 사용자별 GUI 세션 지정이 필요합니다.

```text
Using the default window manager
```

---

## 11. 빠른 복구 절차

### 1단계. XRDP 재시작

```bash
sudo systemctl restart xrdp
sudo systemctl restart xrdp-sesman
```

주의: 전체 XRDP 접속자에게 영향을 줄 수 있으므로 관리자 절차로만 사용합니다.

### 2단계. 사용자 세션 파일 재설정

Rocky Linux:

```bash
echo "startxfce4" > ~/.Xclients
chmod +x ~/.Xclients
```

Ubuntu:

```bash
echo "startxfce4" > ~/.xsession
```

### 3단계. 세션 관련 임시 파일 삭제

```bash
rm -f ~/.Xauthority
rm -f ~/.xsession-errors
```

### 4단계. 재부팅

```bash
sudo reboot
```

---

## 12. 기존 로그인 세션 충돌 해결

현재 로그인 세션 확인:

```bash
loginctl
```

특정 세션 종료:

```bash
loginctl terminate-session 세션번호
```

로컬 모니터에서 동일 계정으로 로그인 중이면 로그아웃 후 XRDP로 다시 접속합니다.

---

## 13. 최종 권장 운영 방식

| 용도 | 권장 방식 |
|---|---|
| GUI 원격 접속 | XRDP + XFCE |
| 텍스트 복사/붙여넣기 | XRDP Clipboard |
| 작은 파일 이동 | XRDP Drive Redirection |
| 큰 파일 이동 | WinSCP / SFTP |
| 개발 작업 | VSCode Remote SSH |
| 서버 안정성 | Wayland 비활성화 |

---

## 14. 결론

XRDP 검은 화면 문제는 대부분 XRDP 자체 문제가 아니라 Linux GUI 세션 문제입니다.

Rocky Linux 또는 Ubuntu 서버에서 안정적으로 사용하려면 다음 조합을 권장합니다.

```text
XRDP + X11 + XFCE + WinSCP
```

GNOME과 Wayland 조합은 서버 원격 GUI 환경에서는 불안정할 수 있으므로, 운영용 서버에서는 XFCE 기반으로 단순하게 구성하는 것이 적절합니다.

---

## 15. 추가 문서

서버별 계정을 개별 생성하지 않고 중앙에서 관리하려면 다음 문서를 참고합니다.

- [중앙 계정 관리 및 서버 계정 동기화 방안](./docs/account-sync/README.md)
- [중앙 계정 동기화 아키텍처](./docs/account-sync/architecture.md)
- [중앙 계정 관리 구축 작업계획서](./docs/account-sync/implementation-plan.md)
- [중앙 계정 관리 운영 기준](./docs/account-sync/operations.md)
