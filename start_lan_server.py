"""
Start the FastAPI server with LAN access
Run this script to allow other devices on your network to access the API
"""
import uvicorn
import socket

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8001
    
    print("🚀 Starting LC Management API Server")
    print("=" * 50)
    print(f"📡 Local access: http://127.0.0.1:{port}")
    print(f"🌐 LAN access: http://{local_ip}:{port}")
    print(f"📚 API docs: http://{local_ip}:{port}/docs")
    print(f"🔍 Health check: http://{local_ip}:{port}/health")
    print("=" * 50)
    print("Share these URLs with your frontend developer:")
    print(f"  API Base URL: http://{local_ip}:{port}")
    print(f"  Login endpoint: http://{local_ip}:{port}/auth/login")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start the server on all interfaces (0.0.0.0)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # This allows external connections
        port=port,
        reload=True,
        log_level="info"
    )
