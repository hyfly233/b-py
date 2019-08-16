import ray

if __name__ == '__main__':
    context = ray.init()
    print(context.dashboard_url)