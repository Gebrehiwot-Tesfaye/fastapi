import redis
import os
from dotenv import load_dotenv

load_dotenv()

def test_redis_connection():
    print("🔍 Testing Redis Connection...")
    
    # Try different Redis URLs
    redis_urls = [
        "redis://localhost:6379",
        "redis://127.0.0.1:6379",
        "redis://0.0.0.0:6379",
    ]
    
    for url in redis_urls:
        print(f"\n📡 Trying to connect to: {url}")
        try:
            client = redis.from_url(url, decode_responses=True, socket_connect_timeout=3)
            client.ping()
            print(f"✅ Successfully connected to Redis at {url}")
            
            # Test basic operations
            test_key = "test_key"
            test_value = "test_value"
            
            # SET operation
            client.set(test_key, test_value, ex=10)
            print(f"💾 SET {test_key} = {test_value}")
            
            # GET operation
            retrieved = client.get(test_key)
            print(f"📖 GET {test_key} = {retrieved}")
            
            # DELETE operation
            client.delete(test_key)
            print(f"🗑️ Deleted {test_key}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to {url}: {e}")
    
    print("\n🚨 All Redis connection attempts failed!")
    print("\n💡 Possible solutions:")
    print("1. Make sure Redis is running in WSL: sudo systemctl status redis-server")
    print("2. Check if Redis is accessible from Windows:")
    print("   - In WSL: redis-cli config get bind")
    print("   - Should show 'bind *' or 'bind 0.0.0.0' for external access")
    print("3. Configure Redis to accept external connections:")
    print("   - Edit /etc/redis/redis.conf")
    print("   - Change 'bind 127.0.0.1' to 'bind 0.0.0.0'")
    print("   - Restart Redis: sudo systemctl restart redis-server")
    print("4. Use Docker Redis instead (recommended for Windows):")
    print("   docker run -d -p 6379:6379 --name redis redis:latest")
    
    return False

if __name__ == "__main__":
    test_redis_connection()
