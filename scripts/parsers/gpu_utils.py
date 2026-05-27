import os
import torch


def has_cuda() -> bool:
    """Проверяет наличие CUDA/GPU"""
    return torch.cuda.is_available()


def get_device_info() -> dict:
    """Возвращает информацию о доступном устройстве"""
    cuda_available = has_cuda()
    
    info = {
        "cuda_available": cuda_available,
        "device": "gpu" if cuda_available else "cpu",
    }
    
    if cuda_available:
        info["device_name"] = torch.cuda.get_device_name(0)
        info["device_count"] = torch.cuda.device_count()
        info["total_memory"] = torch.cuda.get_device_properties(0).total_memory / 1e9  # GB
    
    return info


def should_use_gpu() -> bool:
    """
    Определяет, нужно ли использовать GPU
    Проверяет переменные окружения:
    - NOTABENE_FORCE_GPU=1 - всегда GPU
    - NOTABENE_FORCE_CPU=1 - всегда CPU
    """
    force_gpu = os.getenv("NOTABENE_FORCE_GPU", "0") == "1"
    force_cpu = os.getenv("NOTABENE_FORCE_CPU", "0") == "1"
    
    if force_gpu:
        return True
    if force_cpu:
        return False
    
    return has_cuda()


def print_device_info():
    """Выводит информацию об устройстве"""
    info = get_device_info()
    use_gpu = should_use_gpu()
    
    print(f"🖥️  Device Info:")
    print(f"   CUDA Available: {info['cuda_available']}")
    print(f"   Using: {info['device'].upper()}")
    
    if info['cuda_available']:
        print(f"   GPU: {info['device_name']}")
        print(f"   GPUs: {info['device_count']}")
        print(f"   Memory: {info['total_memory']:.1f} GB")
