# Redis Integration for FastAPI

This guide shows how to integrate Redis caching into your FastAPI application and compare performance before and after Redis.

## 🚀 Setup Instructions

### 1. Install Redis

#### Windows:
```bash
# Using WSL2 (Recommended)
wsl --install
# Then in WSL:
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# OR using Docker
docker run -d -p 6379:6379 --name redis redis:latest
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Linux:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The new dependencies added:
- `redis` - Redis Python client
- `aioredis` - Async Redis support

### 3. Environment Configuration

Your `.env` file should now include:
```
DATABASE_URL=postgresql://postgres:Gebby%400953@localhost/fruitdb
REDIS_URL=redis://localhost:6379
```

### 4. Start the Application

```bash
# Make sure Redis is running first
redis-cli ping  # Should return PONG

# Start FastAPI
python main.py
```

## 🎯 How Redis Caching Works

### Cache Strategy:
- **GET /fruits**: Results are cached for 1 hour (3600 seconds)
- **POST/PUT/DELETE**: Cache is automatically invalidated
- **Cache Key**: `fruits:list`

### Performance Benefits:
- 🚀 **Cache Hit**: ~1-5ms response time
- 🐘 **Cache Miss**: ~20-100ms response time (database query)
- 📈 **Performance Improvement**: 80-95% faster for cached requests

## 📊 Performance Testing

### Run Performance Tests:

```bash
# Install additional testing dependencies
pip install requests matplotlib

# Run the performance test
python performance_test.py
```

### What the Test Does:

1. **Cold Cache Test**: Measures response time when cache is empty
2. **Warm Cache Test**: Measures response time when data is cached
3. **Cache Behavior Analysis**: Compares cache miss vs cache hit performance
4. **Generates Reports**: Creates JSON report and PNG charts

### Expected Results:

```
📊 Cache Analysis:
   First request (cache miss): 45.23ms
   Average cache hit time: 2.15ms
   Performance improvement: 95.2%
```

## 🔧 API Endpoints with Caching

### GET /fruits
```bash
# First request (cache miss)
curl http://localhost:8000/fruits
# Response time: ~45ms
# Logs: 🐘 Database query! Retrieved fruits in 45.23ms

# Second request (cache hit)
curl http://localhost:8000/fruits
# Response time: ~2ms
# Logs: 🚀 Cache hit! Retrieved fruits in 2.15ms
```

### POST /fruits (Cache Invalidation)
```bash
curl -X POST http://localhost:8000/fruits \
  -H "Content-Type: application/json" \
  -d '{"name": "mango", "category": "tropical"}'
# Logs: 🗑️ Cache invalidated after adding fruit
```

### PUT /fruits/{name} (Cache Invalidation)
```bash
curl -X PUT http://localhost:8000/fruits/apple \
  -H "Content-Type: application/json" \
  -d '{"name": "apple", "category": "tree fruit"}'
# Logs: 🗑️ Cache invalidated after updating fruit
```

### DELETE /fruits/{name} (Cache Invalidation)
```bash
curl -X DELETE http://localhost:8000/fruits/banana
# Logs: 🗑️ Cache invalidated after deleting fruit
```

## 🛠️ Redis Configuration Options

### Cache Expiration:
Edit `main.py` line 70:
```python
# Cache for 30 minutes instead of 1 hour
redis_client.set(cache_key, fruit_list, expire=1800)
```

### Redis Connection Settings:
Edit `redis_client.py` to customize:
```python
self.redis_client = redis.from_url(
    redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    max_connections=20  # Add this for connection pooling
)
```

## 📈 Monitoring Redis

### Check Redis Status:
```bash
redis-cli info server
redis-cli info memory
redis-cli info stats
```

### Monitor Cache Usage:
```bash
# Check cached keys
redis-cli keys "*"

# Check cache TTL
redis-cli ttl "fruits:list"

# Monitor Redis in real-time
redis-cli monitor
```

## 🔍 Troubleshooting

### Redis Connection Issues:
1. **Check if Redis is running**: `redis-cli ping`
2. **Verify Redis URL**: Check `.env` file
3. **Check logs**: Application will show Redis connection status

### Cache Not Working:
1. **Check Redis connection**: Look for "✅ Successfully connected to Redis!" in logs
2. **Verify cache key**: Check if `fruits:list` exists in Redis
3. **Manual cache clear**: `redis-cli del "fruits:list"`

### Performance Issues:
1. **Redis memory**: Check `redis-cli info memory`
2. **Network latency**: Ensure Redis is on same machine or fast network
3. **Cache size**: Monitor memory usage with large datasets

## 🎯 Best Practices

1. **Cache Invalidation**: Always clear cache after data modifications
2. **Appropriate TTL**: Set expiration based on data change frequency
3. **Error Handling**: Application gracefully handles Redis failures
4. **Monitoring**: Track cache hit/miss ratios
5. **Memory Management**: Monitor Redis memory usage

## 📚 Additional Resources

- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Caching Guide](https://fastapi.tiangolo.com/advanced/additional-responses/)
- [Redis Python Client](https://redis-py.readthedocs.io/)

## 🎉 You're Ready!

Your FastAPI application now has Redis caching with:
- ✅ Automatic caching for GET requests
- ✅ Smart cache invalidation
- ✅ Performance monitoring
- ✅ Error handling
- ✅ Performance comparison tools

Start your application and enjoy the speed boost! 🚀
