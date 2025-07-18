from adb_auto.utils.redis_helper import r

r.set("foo", "bar")
b = r.get("foo")

assert b == b"bar"
