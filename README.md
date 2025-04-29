# youtrack-export
# 📂 YouTrack Issue Exporter

YouTrack 이슈를 검색, 미리보기, 필터링하고  
엑셀 파일로 저장할 수 있는 데스크탑 GUI 툴입니다.

---

## ✨ 주요 기능

- ✅ 프로젝트 검색 및 선택
- ✅ 이슈 상태, 담당자, 우선순위, 댓글수 등 주요 필드 미리보기
- ✅ 상태 필터링 기능 (전체/Open/In Progress 등)
- ✅ 엑셀(.xlsx)로 저장
- ✅ 설정 파일(config.ini)로 토큰, URL 저장 및 수정
- ✅ GUI 기반 사용자 친화적 인터페이스

---

## 🔑 YouTrack 토큰 발급 방법

1. YouTrack에 로그인합니다.
2. 우측 상단 프로필 사진 클릭 → `Profile`로 이동합니다.
3. `Authentication` (인증) 메뉴로 이동합니다.
4. `New Token` 버튼을 클릭합니다.
5. **Scope(권한)** 설정:  
   - `YouTrack` > `Read Issue`, `Read Project`, `Read User` **필수 선택**
6. 토큰을 생성하고, 발급된 토큰 값을 복사합니다.

> **주의:** 발급된 토큰은 **다시 볼 수 없습니다**. 반드시 복사해 두세요.

---
