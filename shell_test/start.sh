#!/bin/bash

PID_FILE=""
EXEC_FILE=""

# 解析命令行参数
ACTION="$1"
shift

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -p|--pid-file)
        PID_FILE="$2"
        shift # past argument
        shift # past value
        ;;
        -s|--script)
        EXEC_FILE="$2"
        shift # past argument
        shift # past value
        ;;
        *)
        shift # unknown option
        ;;
    esac
done

start() {
    if [ -z "$PID_FILE" ]; then
        echo "Error: No PID file specified."
        exit 1
    fi

    if [ -z "$EXEC_FILE" ]; then
        echo "Error: No Python file specified."
        exit 1
    fi

    PID_DIR=$(dirname "$PID_FILE")

    if [ ! -d "$PID_DIR" ]; then
        mkdir -p "$PID_DIR"
    fi

    if [ -f "$PID_FILE" ]; then
        echo "Application is already running."
        exit 1
    fi

    echo "Starting application with script: $EXEC_FILE"
    nohup "$EXEC_FILE" > "$PID_DIR/app.log" 2>&1 &

    # 后台运行的最后一个进程的进程ID号
    echo $! > "$PID_FILE"

    # 父进程的进程ID号
#    echo $PPID > "$PID_FILE"

    echo "Application started with PID $(cat $PID_FILE)."
}

stop() {
    if [ -z "$PID_FILE" ]; then
        echo "Error: No PID file specified."
        exit 1
    fi

    if [ ! -f "$PID_FILE" ]; then
        echo "Application is not running."
        exit 1
    fi

    PID=$(cat "$PID_FILE")
    echo "Stopping application with PID $PID..."

    kill -9 $PID

    rm "$PID_FILE"
    echo "Application stopped."
}

status() {
    if [ -z "$PID_FILE" ]; then
        echo "Error: No PID file specified."
        exit 1
    fi

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")

        if ps -p $PID > /dev/null; then
            echo "Application is running with PID $PID."
        else
            # 进程被异常中断，pid 文件未被清理
            rm "$PID_FILE"
            echo "Application is not running, but PID file exists."
        fi
    else
            echo "Application is not running."
    fi
}

case "$ACTION" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|status} -p <pid_file> -s <exec_file>"
        exit 1
        ;;
esac