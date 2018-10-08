import multiprocessing
import platform
import sys

import torch


def main():
    # 获取操作系统类型
    os_type = platform.system()
    print("操作系统类型:", os_type)

    # 获取操作系统版本号
    os_version = platform.version()
    print("操作系统版本号:", os_version)

    # 获取操作系统的主机名
    hostname = platform.node()
    print("主机名:", hostname)

    # 获取CPU架构
    cpu_architecture = platform.machine()
    print("CPU架构:", cpu_architecture)

    # 获取CPU核心数
    cpu_cores = multiprocessing.cpu_count()
    print("CPU核心数:", cpu_cores)

    # 获取Python版本
    python_version = sys.version_info
    print("Python版本:", python_version)

    # 获取cuda版本
    cuda_version = torch.version.cuda
    print("CUDA版本:", cuda_version)
    cudnn_version = torch.backends.cudnn.version()
    print("cuDNN版本:", cudnn_version)



if __name__ == '__main__':
    main()
