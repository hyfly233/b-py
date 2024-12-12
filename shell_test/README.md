## 打包程序

```shell
cd ..
pyinstaller -F ./shell_test/test.py
```

## Start.sh

Start.sh 的 start() 在获取 pid 后会将 pid 写入到 pid 文件中，但在多线程中，pid 获取并不准确

1. 使用 `echo $! > "$PID_FILE"` 时
    + 执行 ps 和 lsof 命令
       ```text
       ps -ef | grep test
       
       501 41861     1   0  5:34PM ttys007    0:00.09 ./../dist/test
       501 41863 41861   0  5:34PM ttys007    0:00.48 ./../dist/test
       501 41877 40558   0  5:34PM ttys007    0:00.00 grep test
       
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
       501 42375 40558   0  5:37PM ttys007    0:00.00 grep test
       
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

## 脚本执行

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