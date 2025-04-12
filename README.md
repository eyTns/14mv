# 14mv
 14 minesweeper variants hint calculator with GUI


## 켜는법 (windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\activate # 터미널 활성화를 해놓은 채로 main.py를 실행행
pip install uv

```


# TODOs
- [X] 이미지를 받아오기
- [X] 이미지에서 표로 변환
- [X] 표에서 숫자를 추출 해서 list로 저장
- [ ] list에서 힌트 계산
- [ ] 계산이 완료된 list를 표시
- [ ] TDD 어케함?
- [ ] 사이즈 인식하기
  - 좌상단 꼭짓점이 "6"에서 나오면 그 판의 사이즈는 5임
