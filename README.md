# OdeFrame

OdeFrame은 AION2용 오버레이 트래커입니다.  
서버별 키나 획득률 제한, 캐릭터별 컨텐츠 진행 상황 및 오드에너지 보유량을 한눈에 관리할 수 있으며, 게임 화면의 정보를 OCR로 읽어와 오드 에너지 보유량을 동기화할 수 있습니다.

## 주요 기능

- 서버 공유형 키나 획득률 관리
- 엑셀 형태로 캐릭터별 컨텐츠 체크 및 진행 관리
- OCR 기반 오드 동기화
- 게임 창 감지를 통한 캐릭터 자동 선택
- 오버레이 중심 사용 흐름과 단축키 지원


## 빠른 시작

1. OCR 기능을 사용하기 위해 Tesseract OCR을 먼저 설치합니다.
- [UB Mannheim Windows 빌드](https://github.com/UB-Mannheim/tesseract/wiki)
2. 최신 릴리즈에서 `OdeFrame.exe`를 다운로드합니다.
3. `OdeFrame.exe`를 실행합니다.
4. 단축키 사용을 위해 OdeFrame도 관리자 권한으로 실행하는 것을 권장합니다.


## OCR 설치 경로

OCR 기반 오드 동기화 기능을 사용하려면 Windows에 Tesseract OCR이 설치되어 있어야 합니다.

권장 설치 경로:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`


## 사용 시 참고사항

- OCR 및 단축키 동작은 게임 실행 권한과 입력 환경에 따라 차이가 있을 수 있습니다.
- 기존 데이터는 `C:\Users\<사용자명>\.aion2tracker.json` 파일을 사용합니다.
- 기본 배포 버전에는 Tesseract OCR이 포함되어 있지 않습니다.

## 빌드 방법

실행 파일을 빌드하려면 아래 명령을 사용합니다.

```bat
build.bat
```

빌드 결과물:

- `dist\OdeFrame.exe`

## 바로 실행

빌드없이 바로 실행하려면:

```bat
run.bat
```