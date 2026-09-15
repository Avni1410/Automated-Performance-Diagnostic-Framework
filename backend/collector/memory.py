import psutil

from backend.config import MEMORY_WARNING, MEMORY_CRITICAL


def get_memory_status(percent):
    if percent >= MEMORY_CRITICAL:
        return "Critical"
    elif percent >= MEMORY_WARNING:
        return "Warning"
    else:
        return "Normal"


def get_memory_metrics():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "available_gb": round(memory.available / (1024 ** 3), 2),
        "percent": memory.percent,
        "status": get_memory_status(memory.percent),
        "swap_total_gb": round(swap.total / (1024 ** 3), 2),
        "swap_used_gb": round(swap.used / (1024 ** 3), 2),
        "swap_percent": swap.percent
    }


if __name__ == "__main__":
    metrics = get_memory_metrics()

    print("---- MEMORY MONITORING ----")
    print(f"Total Memory   : {metrics['total_gb']} GB")
    print(f"Used Memory    : {metrics['used_gb']} GB")
    print(f"Available      : {metrics['available_gb']} GB")
    print(f"Usage          : {metrics['percent']}%")
    print(f"Status         : {metrics['status']}")
    print(f"Swap Total     : {metrics['swap_total_gb']} GB")
    print(f"Swap Used      : {metrics['swap_used_gb']} GB")
    print(f"Swap Usage     : {metrics['swap_percent']}%")
