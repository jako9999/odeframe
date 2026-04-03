# OdeFrame

AION2용 오버레이 트래커입니다. 캐릭터별 컨텐츠 체크, 키나/오드 관리, OCR 기반 오드 동기화를 지원합니다.

## 배포 기준

기본 배포 방식은 단일 실행 파일 생성입니다.

- 기본 실행 파일: `OdeFrame.exe`
- 주의: OCR 기능을 사용하려면 사용자가 직접 Tesseract OCR을 설치해야 합니다.

## Tesseract OCR 설치

이 프로젝트의 OCR 기능은 Tesseract OCR이 설치되어 있어야 동작합니다.

- 공식 프로젝트: [Tesseract OCR GitHub](https://github.com/tesseract-ocr/tesseract)
- Windows 설치 안내 참고: [Tesseract Downloads Wiki](https://github.com/tesseract-ocr/tesseract/wiki/Downloads)
- Windows 설치본으로 많이 쓰이는 배포처: [UB Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

설치 후 아래 경로 중 하나에 `tesseract.exe`가 있어야 합니다.

- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

## 빌드

### 기본 빌드

```bat
build.bat
```

출력:

- `dist\OdeFrame.exe`

### 언어 데이터 지정

기본 OCR 언어 데이터 지정값은 `eng`입니다.

```bat
set TESSDATA_LANGS=eng
build.bat
```

## 실행 권장 사항

- 게임이 관리자 권한으로 실행 중이면 이 앱도 관리자 권한으로 실행하는 것을 권장합니다.
- 기존 `.py` 버전과 동일한 JSON 데이터를 사용합니다.
  - `C:\Users\<사용자명>\.aion2tracker.json`
