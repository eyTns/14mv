# 14mv
 14 minesweeper variants hint calculator with GUI


## 켜는법 (windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\activate # 터미널 활성화를 해놓은 채로 main.py를 실행
pip install uv
```

## pyqt5 가 실행이 안되는 문제
```
(14mv) PS C:\Users\[실명]\Documents\GitHub\14mv> & c:/Users/[실명]/Documents/GitHub/14mv/.venv/Scripts/python.exe c:/Users/[실명]/Documents/GitHub/14mv/main.py
qt.qpa.plugin: Could not find the Qt platform plugin "windows" in ""
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
```
- 경로에 한글이 있어서 그렇다고 한다.
  - https://blog.naver.com/blueqnpfr1/221582202946
- 유저명 바꿔야지...





# TODOs
- [X] 이미지를 받아오기
- [X] 이미지에서 표로 변환
- [X] 표에서 숫자를 추출 해서 list로 저장
- [ ] list에서 힌트 계산
- [ ] 계산이 완료된 list를 표시
- [ ] TDD 어케함?
- [ ] 사이즈 인식하기
  - 좌상단 꼭짓점이 "6"에서 나오면 그 판의 사이즈는 5임

- [ ] 코드가 init에 전부 있는게 보기 안좋으므로 리팩토링
- [ ] 재귀적으로 여러번 실행해서 결과 표시
- [ ] 안전한 칸과 깃발 꽂을 칸을 표로 / 이미지로 표시
- [ ] 해당하는 칸을 자동으로 클릭하기
- [ ] 주석 정리좀


