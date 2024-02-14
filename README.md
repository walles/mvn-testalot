# mvn-testalot

Run `mvn test` multiple times and report on slow / flaky tests.

# Example commands

Run `mvn test` 10 times:
```
mvn-testalot.py 10
```

Analyze results:
```
mvn-testalot.py report
```

# Example output

Output is printed as human readable Markdown, for easy Github bug reporting.

# Slow tests

| Result | Duration | Name |
|--------|----------|------|
| ResultKind.PASS | 0:02:01.153000 | `redis.clients.jedis.tests.JedisSentinelTest.sentinelFailover()` |
| ResultKind.FAIL | 0:00:29.125000 | `redis.clients.jedis.tests.JedisSentinelPoolTest.returnResourceDestroysResourceOnException()` |
| ResultKind.PASS | 0:00:06.176000 | `redis.clients.jedis.tests.JedisClusterTest.testReadonly()` |
| ResultKind.PASS | 0:00:06.149000 | `redis.clients.jedis.tests.SSLJedisClusterTest.testReadonly()` |
| ResultKind.PASS | 0:00:06.070000 | `redis.clients.jedis.tests.SSLJedisClusterWithCompleteCredentialsTest.testReadonly()` |
| ResultKind.PASS | 0:00:04.136000 | `redis.clients.jedis.tests.ShardedJedisPoolWithCompleteCredentialsTest.shouldReturnActiveShardsWhenOneGoesOffline()` |
| ResultKind.PASS | 0:00:04.070000 | `redis.clients.jedis.tests.ShardedJedisPoolTest.shouldReturnActiveShardsWhenOneGoesOffline()` |
| ResultKind.PASS | 0:00:03.378000 | `redis.clients.jedis.tests.JedisSentinelPoolTest.ensureSafeTwiceFailover()` |

# Flaky tests

`.` = pass, `x` = fail, `E` = error

| Result | Name |
|--------|------|
| `x................xx..x........x...` | `redis.clients.jedis.tests.JedisPoolTest.testCloseConnectionOnMakeObject()` |
| `....E.EE.EEE..EEEE.E.EE.E.E.EEEEE.` | `redis.clients.jedis.tests.JedisSentinelPoolTest.checkCloseableConnections()` |
| `....E.EE.EEE..EEEE.E.EE.E.E.EEEEE.` | `redis.clients.jedis.tests.JedisSentinelPoolTest.checkResourceIsCloseable()` |
| `.EEEEEEEEEEEEEEEEEEEEEEEE.EEEEEEEE` | `redis.clients.jedis.tests.JedisSentinelPoolTest.ensureSafeTwiceFailover()` |
| `.xxx` | `redis.clients.jedis.tests.JedisSentinelPoolTest.returnResourceDestroysResourceOnException()` |
| `....E.EE.EEE..EEEE.E.EE.E.E.EEEEE.` | `redis.clients.jedis.tests.JedisSentinelPoolTest.returnResourceShouldResetState()` |
| `.....E.EEEE.EE.E.EE.E.EE...E.E..EE` | `redis.clients.jedis.tests.JedisSentinelPoolWithCompleteCredentialsTest.checkCloseableConnections()` |
| `.....E.EEEE.EE.E.EE.E.EE...E.E..EE` | `redis.clients.jedis.tests.JedisSentinelPoolWithCompleteCredentialsTest.checkResourceIsCloseable()` |
| `.EEEEEE.E..EEEE.E.EEEE.EE.EEEEEE.E` | `redis.clients.jedis.tests.JedisSentinelPoolWithCompleteCredentialsTest.ensureSafeTwiceFailover()` |
| `.....E.EEEE.EE.E.EE.E.EE...E.E..EE` | `redis.clients.jedis.tests.JedisSentinelPoolWithCompleteCredentialsTest.returnResourceShouldResetState()` |
| `.................x................` | `redis.clients.jedis.tests.JedisTest.timeoutConnection()` |
| `.................xx...............` | `redis.clients.jedis.tests.JedisTest.timeoutConnectionWithURI()` |
| `................xxxxxxxxx.........` | `redis.clients.jedis.tests.ShardedJedisPoolTest.shouldReturnActiveShardsWhenOneGoesOffline()` |
| `.................xxxxxx.x.........` | `redis.clients.jedis.tests.ShardedJedisPoolWithCompleteCredentialsTest.shouldReturnActiveShardsWhenOneGoesOffline()` |
| `...............x..................` | `redis.clients.jedis.tests.commands.ControlCommandsTest.clientPause()` |
