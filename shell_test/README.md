
## pyinstaller

### 打包程序

```shell
cd ..
pyinstaller -F ./shell_test/test.py
```

### Start.sh

Start.sh 的 start() 在获取 pid 后会将 pid 写入到 pid 文件中，但在多线程中，pid 获取并不准确

1. 使用 `echo $! > "$PID_FILE"` 时
    + 执行 ps 和 lsof 命令
       ```text
       ps -ef | grep test
       
       501 41861     1   0  5:34PM ttys007    0:00.09 ./../dist/test
       501 41863 41861   0  5:34PM ttys007    0:00.48 ./../dist/test
       
       lsof -i tcp:23333
       
       COMMAND   PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
       test    41863 flyhy   10u  IPv4 0x563e59e391aada47      0t0  TCP *:23333 (LISTEN)
       
       lsof -i tcp:23334
       
       COMMAND   PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
       test    41863 flyhy   11u  IPv4 0xe06f7b785e7620b3      0t0  TCP *:23334 (LISTEN)
       ```
    + 执行 start.sh 的 stop 后
       ```text
       ps -ef | grep test
       
       501 41863     1   0  5:34PM ttys007    0:01.08 ./../dist/test
       
       lsof -i tcp:23333
       
       COMMAND   PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
       test    41863 flyhy   10u  IPv4 0x563e59e391aada47      0t0  TCP *:23333 (LISTEN)
       
       lsof -i tcp:23334
       
       COMMAND   PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
       test    41863 flyhy   11u  IPv4 0xe06f7b785e7620b3      0t0  TCP *:23334 (LISTEN)
       ```
    + 进程 41863 仍然存在，使用 curl 命令如 `curl http://0.0.0.0:23333/test/getPort` 时，会返回 23333 或 23334
    + 只能通过 kill 命令杀死进程 41863

2. 使用 `echo $PPID > "$PID_FILE"` 时
    + pid 文件中的 pid 不是 test 应用的 pid，如 pid 文件中的 pid 为 40558
      ```text
      ps -ef | grep 40558
      
      501 40558 28143   0  5:29PM ttys007    0:00.19 /bin/zsh --login -i
      
      ps -ef | grep test
      
      501 45252     1   0  5:49PM ttys007    0:00.08 ./../dist/test
      501 45256 45252   0  5:49PM ttys007    0:01.12 ./../dist/test
      ```

3. 使用 `echo $$ > "$PID_FILE"` 时
    + pid 文件中的 pid 不是 test 应用的 pid，如 pid 文件中的 pid 为 46092
      ```text
      ps -ef | grep 46092
      # 无输出
      
      ps -ef | grep test
      
      501 46094     1   0  5:55PM ttys007    0:00.10 ./../dist/test
      501 46097 46094   0  5:55PM ttys007    0:00.62 ./../dist/test
      ```

### 脚本执行

启动脚本

```shell
./start.sh start -p ./test.pid -s ./../dist/test
```

停止脚本

```shell
./start.sh stop -p ./test.pid
```

查看状态

```shell
./start.sh status -p ./test.pid
```

### 测试结果
https://github.com/muziing/pyinstaller-docs-zh-cn/blob/main/doc-zh/Markdown/operating-mode.md

使用 pyinstaller 打包的程序，在启动时，会有两个进程，一个是 PyInstaller bootloader，一个是 Python 程序本身。PyInstaller 打包的捆绑程序总是在 PyInstaller bootloader（引导加载程序）中开始执行。当启动程序时，其实就是在运行 Bootloader。Bootloader 会创建一个临时 Python 环境，然后执行对应的脚本。

## nuitka

```shell
nuitka --standalone --onefile --output-dir=./dist ./shell_test/test.py
```

```text
ps -ef | grep test.bin

  501  3737 97716   0  4:25PM ttys004    0:00.16 ./dist/test.bin
  501  3740  3737   0  4:25PM ttys004    0:00.54 /Users/flyhy/workspace/hyfly233/py/b-py/dist/test.bin
  501  4367  3786   0  4:26PM ttys007    0:00.00 grep test.bin
```