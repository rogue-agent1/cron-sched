from cron_sched import CronExpr, explain
import time
c = CronExpr("*/5 * * * *")
assert 0 in c.minute and 5 in c.minute and 10 in c.minute
c2 = CronExpr("0 9 * * 1-5")
assert c2.hour == {9}
assert c2.dow == {1,2,3,4,5}
nxt = c.next_run()
assert nxt is not None
e = explain("0 9 * * 1-5")
assert "hour 9" in e
print("Cron scheduler tests passed")