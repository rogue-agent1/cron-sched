#!/usr/bin/env python3
"""cron_sched — Lightweight task scheduler using cron expressions."""
import sys, os, time, re, argparse, subprocess, json, signal
from datetime import datetime, timedelta
from pathlib import Path

def match_field(field, value, lo, hi):
    if field == '*': return True
    for part in field.split(','):
        step = 1
        if '/' in part: part, step = part.split('/'); step = int(step)
        if part == '*':
            if value % step == 0: return True
        elif '-' in part:
            a, b = map(int, part.split('-'))
            if a <= value <= b and (value - a) % step == 0: return True
        elif int(part) == value: return True
    return False

def matches_cron(expr, dt):
    fields = expr.split()
    if len(fields) != 5: return False
    m, h, dom, mon, dow = fields
    return (match_field(m, dt.minute, 0, 59) and match_field(h, dt.hour, 0, 23) and
            match_field(dom, dt.day, 1, 31) and match_field(mon, dt.month, 1, 12) and
            match_field(dow, dt.weekday(), 0, 6))

def cmd_run(args):
    with open(args.config) as f: jobs = json.load(f)
    print(f'Scheduler started with {len(jobs)} jobs')
    for j in jobs: print(f'  {j["schedule"]:20s} {j["command"]}')
    
    running = True
    def stop(s,f): nonlocal running; running = False
    signal.signal(signal.SIGINT, stop); signal.signal(signal.SIGTERM, stop)
    
    while running:
        now = datetime.now()
        for job in jobs:
            if matches_cron(job['schedule'], now):
                print(f'[{now:%H:%M}] Running: {job["command"]}')
                subprocess.Popen(job['command'], shell=True)
        time.sleep(60 - now.second)

def cmd_test(args):
    now = datetime.now()
    for i in range(args.count):
        dt = now + timedelta(minutes=i)
        if matches_cron(args.expr, dt):
            print(f'  {dt:%Y-%m-%d %H:%M %a}')

def cmd_init(args):
    template = [
        {"schedule": "0 9 * * 1-5", "command": "echo 'Good morning!'"},
        {"schedule": "*/5 * * * *", "command": "echo 'Every 5 minutes'"},
    ]
    print(json.dumps(template, indent=2))

def main():
    p = argparse.ArgumentParser(description='Lightweight cron scheduler')
    s = p.add_subparsers(dest='cmd', required=True)
    sr = s.add_parser('run'); sr.add_argument('config'); sr.set_defaults(func=cmd_run)
    st = s.add_parser('test'); st.add_argument('expr'); st.add_argument('--count',type=int,default=10); st.set_defaults(func=cmd_test)
    s.add_parser('init').set_defaults(func=cmd_init)
    a = p.parse_args(); a.func(a)

if __name__=='__main__': main()
