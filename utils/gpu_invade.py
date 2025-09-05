import torch
import time
import argparse
from multiprocessing import Process
import subprocess
import getpass

# Hàm lấy danh sách user đang sử dụng GPU
def get_gpu_users(cuda_id):
    """Lấy tập hợp các user đang sử dụng GPU với cuda_id."""
    cmd = f"nvidia-smi --query-compute-apps=pid --format=csv,noheader --id={cuda_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"CUDA:{cuda_id} - Lỗi khi chạy nvidia-smi")
        return set()
    
    # Lấy danh sách PID từ nvidia-smi
    pids = result.stdout.strip().split('\n')
    pids = [pid.strip() for pid in pids if pid.strip()]
    if not pids:
        return set()
    
    # Lấy user từ mỗi PID
    users = set()
    for pid in pids:
        cmd = f"ps -o user= -p {pid}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            user = result.stdout.strip()
            if user:
                users.add(user)
    return users

# Hàm cấp phát bộ nhớ GPU
def allocate_gpu_memory(cuda_id, spare_mem=0.5, wtime=5):
    """Quản lý bộ nhớ GPU: cấp phát khi có user khác, giải phóng khi chỉ còn chủ nhân."""
    owner = getpass.getuser()  # Lấy user chạy script (chủ nhân)
    device = torch.device(f"cuda:{cuda_id}")
    allocation_tensor = None  # Biến theo dõi tensor đã cấp phát

    while True:
        with torch.cuda.device(device):
            # Lấy danh sách user hiện tại trên GPU
            users = get_gpu_users(cuda_id)
            print(f"CUDA:{cuda_id} - Người dùng hiện tại: {users}")

            if users - {owner}:  # Nếu có user khác ngoài chủ nhân
                if allocation_tensor is None:  # Nếu chưa cấp phát bộ nhớ
                    free_memory, total_memory = torch.cuda.mem_get_info()
                    print(f"CUDA:{cuda_id} - Tổng bộ nhớ GPU: {total_memory / (1024 ** 3):.2f} GB, Bộ nhớ trống: {free_memory / (1024 ** 3):.2f} GB")
                    
                    # Tính bộ nhớ cần cấp phát, để lại spare_mem GB trống
                    spare = int(spare_mem * (1024 ** 3))
                    memory_to_allocate = free_memory - spare
                    
                    if memory_to_allocate > 0:
                        try:
                            tensor_size = memory_to_allocate // 4  # 4 bytes mỗi float32
                            allocation_tensor = torch.empty(tensor_size, dtype=torch.float32, device=device)
                            print(f"CUDA:{cuda_id} - Đã cấp phát khoảng {memory_to_allocate / (1024 ** 3):.2f} GB, để lại {spare_mem} GB trống.")
                        except RuntimeError as e:
                            print(f"CUDA:{cuda_id} - Lỗi khi cấp phát bộ nhớ: {e}")
                            allocation_tensor = None
            else:  # Nếu chỉ có chủ nhân hoặc không có ai
                if allocation_tensor is not None:  # Nếu đang giữ bộ nhớ
                    del allocation_tensor
                    allocation_tensor = None
                    print(f"CUDA:{cuda_id} - Đã giải phóng bộ nhớ.")
        
        time.sleep(wtime)  # Đợi trước khi kiểm tra lại

# Hàm chính
def main():
    parser = argparse.ArgumentParser(description="Quản lý bộ nhớ GPU dựa trên user.")
    parser.add_argument(
        "--cuda_ids",
        type=int,
        nargs="+",
        default=[1, 3, 4, 5],
        help="Danh sách các ID thiết bị CUDA.",
    )
    parser.add_argument(
        "--spare_mem",
        type=float,
        default=0.5,
        help="Số GB bộ nhớ để lại trống.",
    )
    parser.add_argument(
        "--time",
        type=float,
        default=5,
        help="Thời gian chờ giữa các lần kiểm tra (giây).",
    )
    
    args = parser.parse_args()
    processes = []
    
    # Khởi động một tiến trình riêng cho mỗi GPU
    for cuda_id in args.cuda_ids:
        p = Process(target=allocate_gpu_memory, args=(cuda_id, args.spare_mem, args.time))
        p.start()
        processes.append(p)
    
    # Chờ tất cả tiến trình hoàn thành
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()