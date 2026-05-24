## Todo:
# Dead line 21-05-2026
- Preprocessing==>SMPLest-x, Datase==>Render gloss, Text2Motion==>Render sentence
- tooltip (selected frame setting ui) for mark frame_start, frame_end to easy ✅
- sentences ui and render ✅
- render solution for speed up to generate video
- keypoint extracttion with sepains and manual remark point
# Bonus
- Render option
- Render 3d motion tab
- cmd subprocess 


def get_gpu_stats(*args):
    if not shutil.which("nvidia-smi"):
        return {"hasNvidiaSmi": False, "gpus": []}

    try:
        cmd = "nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used,power.draw,power.limit,clocks.current.graphics,clocks.current.memory,fan.speed --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True, text=True)
        
        gpus = []
        for line in output.strip().split('\n'):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 13:
                gpus.append({
                    "index": int(parts[0]), "name": parts[1], "temperature": int(parts[2]),
                    "utilization": {"gpu": int(parts[3]), "memory": int(parts[4])},
                    "memory": {"total": int(parts[5]), "free": int(parts[6]), "used": int(parts[7])},
                    "power": {"draw": float(parts[8]), "limit": float(parts[9])},
                    "clocks": {"graphics": int(parts[10]), "memory": int(parts[11])},
                    "fan": {"speed": int(parts[12]) if parts[12].isdigit() else 0}
                })
        return {"hasNvidiaSmi": True, "gpus": gpus, "error": None}
    except Exception as e:
        return {"hasNvidiaSmi": False, "gpus": [], "error": str(e)}
