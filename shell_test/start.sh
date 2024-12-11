#!/bin/bash

PID_FILE=""
EXEC_FILE=""
EXEC_ARGS=""
BOOLEAN_MODE=false

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
        -arg|--arguments)
        EXEC_ARGS="$2"
        shift # past argument
        shift # past value
        ;;
        -b|--boolean)
        BOOLEAN_MODE=true
        shift # past argument
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

    echo "Starting application with script: $EXEC_FILE and arguments: $EXEC_ARGS"
    nohup "$EXEC_FILE" $EXEC_ARGS > "$PID_DIR/app.log" 2>&1 &
    echo $! > "$PID_FILE"
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

        if [ "$BOOLEAN_MODE" = false ]; then
            if ps -p $PID > /dev/null; then
                echo "Application is running with PID $PID."
            else
                # 进程被异常中断，pid 文件未被清理
                rm "$PID_FILE"
                echo "Application is not running, but PID file exists."
            fi
        else
            if ps -p $PID > /dev/null; then
                echo "true"
            else
                # 进程被异常中断，pid 文件未被清理
                rm "$PID_FILE"
                echo "false"
            fi
        fi

    else
        if [ "$BOOLEAN_MODE" = true ]; then
            echo "false"
        else
            echo "Application is not running."
        fi
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
        echo "Usage: $0 {start|stop|status} -p <pid_file> -s <exec_file> -arg <exec_args>"
        exit 1
        ;;
esac