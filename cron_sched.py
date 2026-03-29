#!/usr/bin/env python3
"""Cron expression parser and scheduler. Zero dependencies."""
import time, sys, re

class CronExpr:
    def __init__(self, expr):
        parts = expr.strip().split()
        assert len(parts) == 5, f"Need 5 fields, got {len(parts)}"
        self.minute = self._parse_field(parts[0], 0, 59)
        self.hour = self._parse_field(parts[1], 0, 23)
        self.dom = self._parse_field(parts[2], 1, 31)
        self.month = self._parse_field(parts[3], 1, 12)
        self.dow = self._parse_field(parts[4], 0, 6)

    def _parse_field(self, field, lo, hi):
        values = set()
        for part in field.split(","):
            if part == "*":
                values.update(range(lo, hi+1))
            elif "/" in part:
                base, step = part.split("/")
                start = lo if base == "*" else int(base)
                values.update(range(start, hi+1, int(step)))
            elif "-" in part:
                a, b = part.split("-")
                values.update(range(int(a), int(b)+1))
            else:
                values.add(int(part))
        return values

    def matches(self, dt=None):
        if dt is None:
            dt = time.localtime()
        elif isinstance(dt, (int, float)):
            dt = time.localtime(dt)
        return (dt.tm_min in self.minute and dt.tm_hour in self.hour and
                dt.tm_mday in self.dom and dt.tm_mon in self.month and
                dt.tm_wday in self.dow)

    def next_run(self, after=None):
        t = int(after or time.time())
        t = t - (t % 60) + 60  # next minute
        for _ in range(525960):  # max 1 year
            if self.matches(t):
                return t
            t += 60
        return None

def explain(expr):
    c = CronExpr(expr)
    parts = []
    def desc(vals, lo, hi, name):
        if vals == set(range(lo, hi+1)): return f"every {name}"
        return f"{name} " + ",".join(str(v) for v in sorted(vals))
    parts.append(desc(c.minute, 0, 59, "minute"))
    parts.append(desc(c.hour, 0, 23, "hour"))
    parts.append(desc(c.dom, 1, 31, "day"))
    parts.append(desc(c.month, 1, 12, "month"))
    dow_names = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    if c.dow == set(range(0,7)):
        parts.append("every day of week")
    else:
        parts.append("on " + ",".join(dow_names[d] for d in sorted(c.dow)))
    return "; ".join(parts)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Cron parser")
    p.add_argument("expr", nargs="?", default="*/5 * * * *")
    args = p.parse_args()
    c = CronExpr(args.expr)
    print(f"Expression: {args.expr}")
    print(f"Explanation: {explain(args.expr)}")
    nxt = c.next_run()
    if nxt: print(f"Next run: {time.strftime('%Y-%m-%d %H:%M', time.localtime(nxt))}")
