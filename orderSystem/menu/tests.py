import redis

try:
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    r.ping()
    print("✅ Redis 连接成功！")
except Exception as e:
    print("❌ Redis 连接失败：", e)
