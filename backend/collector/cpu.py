import psutil

from backend.config import CPU_WARNING, CPU_CRITICAL


def get_cpu_status(percent):
    if percent >= CPU_CRITICAL:
        return "Critical"
    elif percent >= CPU_WARNING:
        return "Warning"
    else:
        return "Normal"


def get_cpu_metrics():
    total_cpu = psutil.cpu_percent(interval=1)
    per_core = psutil.cpu_percent(interval=1, percpu=True)

    return {
        "total_percent": total_cpu,
        "status": get_cpu_status(total_cpu),
        "per_core_percent": per_core,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True)
    }


if __name__ == "__main__":
    metrics = get_cpu_metrics()

    print("---- CPU MONITORING ----")
    print(f"Total CPU Usage : {metrics['total_percent']}%")
    print(f"Status          : {metrics['status']}")
    print(f"Physical Cores  : {metrics['physical_cores']}")
    print(f"Logical Cores   : {metrics['logical_cores']}")

    print("Per-Core Usage:")
    for index, usage in enumerate(metrics["per_core_percent"]):
        print(f"Core {index}: {usage}%")
