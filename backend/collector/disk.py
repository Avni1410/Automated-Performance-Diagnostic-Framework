import psutil

from backend.config import DISK_WARNING, DISK_CRITICAL


def get_disk_status(percent):
    if percent >= DISK_CRITICAL:
        return "Critical"
    elif percent >= DISK_WARNING:
        return "Warning"
    else:
        return "Normal"


def get_disk_metrics():
    disk = psutil.disk_usage("/")

    return {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent,
        "status": get_disk_status(disk.percent)
    }


if __name__ == "__main__":
    metrics = get_disk_metrics()

    print("---- DISK MONITORING ----")
    print(f"Total Disk : {metrics['total_gb']} GB")
    print(f"Used Disk  : {metrics['used_gb']} GB")
    print(f"Free Disk  : {metrics['free_gb']} GB")
    print(f"Usage      : {metrics['percent']}%")
    print(f"Status     : {metrics['status']}")
