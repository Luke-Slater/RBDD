import subprocess

pairs = [(6,6),(8, 8), (10, 10), (12, 12), (14, 14), (16, 16), (18, 18), 
         (20, 20), (30, 30), (40, 40), (50, 50), (60, 60), (60, 80), 
         (60, 100), (60, 120), (80, 60), (80, 80), (80, 120), (80, 160), 
         (100, 60), (100, 100), (100, 160), (100, 200), (120, 60), 
         (120, 80), (120, 120), (120, 160), (120, 200)]
pairs = [(6,6),(8,8),(10,10),(12,12),(14,14),(16,16),(18,18),(20,20)]

for pair in pairs:
    command = ["python3", "SCRIPTS/PAR_BUILD_QUERIES.py", str(pair[0]), str(pair[1])]

    result = subprocess.run(command, capture_output=False)
    