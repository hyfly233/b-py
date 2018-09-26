import logging
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
_log = logging.getLogger(__name__)


def main():
    # 判断运行的平台 macos windows linux
    os_platform = os.uname().sysname

    _log.info("运行平台: %s", os_platform)


if __name__ == '__main__':
    main()
