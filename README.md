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
- [O] 이미지를 받아오기
- [O] 이미지에서 표로 변환
- [O] 표에서 숫자를 추출 해서 list로 저장
- [O] list에서 힌트 계산
- [O] 계산이 완료된 list를 표시
- [O] 해당하는 칸을 자동으로 클릭하기
- [O] window.py 코드가 init에 전부 있는게 보기 안좋으므로 리팩토링
- [X] 안전한 칸과 깃발 꽂을 칸을 표로 / 이미지로 표시
- [O] 로깅, 주석 정리좀
- [O] 다음 스테이지로 자동으로 넘어가기
- [O] 숫자 하나를 클릭하면 되는것은 그걸 클릭하기
- [O] 14mv2와 이미지 픽셀 다른데 해결하기
- [O] 멈춰야 되는 조건 적용하기
- [O] 클릭 배치처리로 반복시간 줄이기
- [X] 힌트만으로 못풀었으면 문제 그냥 넘기고 계속 진행하기
- [O] V!, X, X', X'!, K, K! 보드정보 입력하기
- [O] 재생 표시가 있을때 스페이스바 누르고 넘어가고 리캡쳐
- [X] TDD 어케함?
- [ ] GUI 창에서 사이즈 선택할수 있게 하기
- [ ] 사이즈 인식하기
  - 좌상단 꼭짓점이 "6"에서 나오면 그 판의 사이즈는 5임
- [ ] 전체 칸에 대한 개수 세서 활용해서 풀기
  - 각 모드+사이즈 별 지뢰 개수 입력 필요
- [ ] 재귀적으로 여러번 실행해서 결과 표시
- [ ] area2 in (area1 + area3) 인 경우 검사하기
  - 1과 3은 안겹치고 2는 union(1, 3) 안에 들어가면 1+3-2 영역을 본다