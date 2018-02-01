## uv 操作

+ uv init
+ uv venv --python 3.13
+ uv sync / uv pip install pysnmplib -i https://pypi.tuna.tsinghua.edu.cn/simple / uv add pysnmplib
+ uv tree
+ uv pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  # 从 requirements.txt 文件中安装 
+ uv pip freeze > requirements.txt  # 依赖保存到文件
+ uv run main.py
+ uv lock --upgrade-package requests

## 打包
```shell
pyinstaller -F --clean test.py

pyinstaller -F test.py
```