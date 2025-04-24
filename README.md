# 14mv
 14 minesweeper variants hint calculator with GUI


## 켜는법 (windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\activate # 터미널 활성화를 해놓은 채로 main.py를 실행

deactivate
C:\dev\14mv\.venv\Scripts\activate

pip install uv

uv add pydantic
uv add --active pydantic
```

## pyqt5 가 실행이 안되는 문제
```
(14mv) PS C:\Users\[실명]\Documents\GitHub\14mv> & c:/Users/[실명]/Documents/GitHub/14mv/.venv/Scripts/python.exe c:/Users/[실명]/Documents/GitHub/14mv/main.py
qt.qpa.plugin: Could not find the Qt platform plugin "windows" in ""
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
```
- 경로에 한글이 있어서 그렇다고 한다.
  - https://blog.naver.com/blueqnpfr1/221582202946
- C:\dev\14mv 에 따로 설치했다.





# TODOs
## Todo
- 재귀적으로 여러번 실행해서 결과 표시
- 14mv2 문제들 풀기
- GUI 창에서 사이즈 선택할수 있게 하기
- 사이즈 인식하기
  - 좌상단 꼭짓점이 "6"에서 나오면 그 판의 사이즈는 5임
- 똑같은 리전이 저장될거같은데 중복검사하기
- 영역 덧셈하기
- 리팩토링: 새 규칙 추가하기 쉽게
- 리팩토링: 디스플레이, 조작하는 함수 파일 옮기기
- 리팩토링: 주석 빼
- 리팩토링: 테스트들 점검
- 리팩토링: 안쓰는 함수 지우기
- A in (B 합 C) 이고 (B교C 의 칸 수) = (B needed) = (C needed) = k>0 이면 B교C는 safe이다.
- "트리플 셀" 의 듀얼 로직 구현하기기

## Done
- ✅ 이미지를 받아오기
- ✅ 이미지에서 표로 변환
- ✅ 표에서 숫자를 추출 해서 list로 저장
- ✅ list에서 힌트 계산
- ✅ 계산이 완료된 list를 표시
- ✅ 해당하는 칸을 자동으로 클릭하기
- ✅ window.py 코드가 init에 전부 있는게 보기 안좋으므로 리팩토링
- ✅ 로깅, 주석 정리좀
- ✅ 다음 스테이지로 자동으로 넘어가기
- ✅ 숫자 하나를 클릭하면 되는것은 그걸 클릭하기
- ✅ 멈춰야 되는 조건 적용하기
- ✅ 클릭 배치처리로 반복시간 줄이기
- ✅ V!, X, X', X'!, K, K! 보드정보 입력하기
- ✅ 재생 표시가 있을때 스페이스바 누르고 넘어가고 리캡쳐
- ✅ 전체 칸에 대한 개수 세서 활용해서 풀기
  - 각 모드+사이즈 별 지뢰 개수 입력 필요
- ✅ B 유형 풀기
- ✅ area2 in (area1 + area3) 인 경우 검사하기
  - 1과 3은 안겹치고 2는 union(1, 3) 안에 들어가면 1+3-2 영역을 본다
- 트리플 힌트 일반적인 경우 만들기
- 좀더 제너럴한 region 3개 검사하기
- A교B, A교C, B교C가 존재하고 B, C의 needed는 둘다 1이고 A의 needed는 수-1 이면 B교C는 safe이다.

## Not to do
- ❌ 안전한 칸과 깃발 꽂을 칸을 표로 / 이미지로 표시
- ❌ 힌트만으로 못풀었으면 문제 그냥 넘기고 계속 진행하기
- ❌ TDD 어케함?
- ❌ 쿼드루플 힌트 (둘둘짝) 만들기 (X'! 풀기)
- 싱글 힌트 클릭 부활시키기
