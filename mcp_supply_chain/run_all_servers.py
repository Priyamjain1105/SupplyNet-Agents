import subprocess
import sys
import os
import time

# Ensure UTF-8 output encoding on Windows
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVERS = [
    ("News Server", os.path.join(BASE_DIR, "servers", "news_server.py"), 8001),
    ("Weather Server", os.path.join(BASE_DIR, "servers", "weather_server.py"), 8002),
    ("Toll RAG Server", os.path.join(BASE_DIR, "servers", "toll_rag_server.py"), 8003),
    ("OSRM Server", os.path.join(BASE_DIR, "servers", "osrm_server.py"), 8004),
]

def main():
    print("=========================================================")
    print(" Launching Multi-Server MCP Architecture (4 Servers)")
    print("=========================================================\n")
    
    python_exe = sys.executable
    processes = []
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"

    try:
        for name, script_path, port in SERVERS:
            abs_path = os.path.abspath(script_path)
            print(f"Starting {name} on http://localhost:{port}/mcp ({script_path})...")
            proc = subprocess.Popen([python_exe, abs_path], env=child_env)
            processes.append((name, proc))
            time.sleep(1)

        print("\nAll 4 MCP Servers are running!")
        print("Press Ctrl+C to stop all servers.\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping all MCP servers...")
        for name, proc in processes:
            proc.terminate()
            print(f"Stopped {name}.")
        print("Done.")

if __name__ == "__main__":
    main()
