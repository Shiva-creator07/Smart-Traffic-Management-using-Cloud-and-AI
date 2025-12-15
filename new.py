import subprocess
import requests
import socket

CAMERA_IP = "192.168.29.159"
CAMERA_PORT = "8080"

print("="*60)
print("Network Connectivity Diagnostic")
print("="*60)

# Test 1: Ping
print("\n1. Testing ping to camera...")
try:
    result = subprocess.run(['ping', '-c', '3', CAMERA_IP], 
                          capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print(f"   ✓ Camera is reachable at {CAMERA_IP}")
    else:
        print(f"   ❌ Cannot ping {CAMERA_IP}")
        print("   Reason: Phone and Mac are on different networks")
except Exception as e:
    print(f"   ❌ Ping failed: {e}")

# Test 2: Port check
print(f"\n2. Testing port {CAMERA_PORT}...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((CAMERA_IP, int(CAMERA_PORT)))
    sock.close()
    
    if result == 0:
        print(f"   ✓ Port {CAMERA_PORT} is open")
    else:
        print(f"   ❌ Port {CAMERA_PORT} is closed or blocked")
        print("   Reason: IP Webcam app not running or firewall blocking")
except Exception as e:
    print(f"   ❌ Port check failed: {e}")

# Test 3: HTTP request
print(f"\n3. Testing HTTP connection...")
try:
    url = f"http://{CAMERA_IP}:{CAMERA_PORT}"
    response = requests.get(url, timeout=5)
    print(f"   ✓ HTTP connection successful (Status: {response.status_code})")
except requests.exceptions.Timeout:
    print(f"   ❌ Connection timeout - Camera not responding")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Connection refused - No route to host")
    print("\n   PROBLEM IDENTIFIED: Cannot reach phone from Mac")
except Exception as e:
    print(f"   ❌ HTTP failed: {e}")

# Test 4: Your Mac's IP
print("\n4. Your Mac's network info...")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    mac_ip = s.getsockname()[0]
    s.close()
    print(f"   Your Mac IP: {mac_ip}")
    print(f"   Camera IP:   {CAMERA_IP}")
    
    # Check if on same network
    mac_network = '.'.join(mac_ip.split('.')[:3])
    camera_network = '.'.join(CAMERA_IP.split('.')[:3])
    
    if mac_network == camera_network:
        print(f"   ✓ Both on same network: {mac_network}.x")
    else:
        print(f"   ❌ Different networks:")
        print(f"      Mac: {mac_network}.x")
        print(f"      Camera: {camera_network}.x")
        print("\n   SOLUTION: Connect both to the same WiFi network!")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
