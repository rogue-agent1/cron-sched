# cron_sched

Lightweight task scheduler using cron expressions. JSON config, test mode.

## Usage

```bash
python3 cron_sched.py init > jobs.json   # Generate template
python3 cron_sched.py run jobs.json      # Start scheduler
python3 cron_sched.py test "0 9 * * 1-5" --count 10  # Preview schedule
```

## Zero dependencies. Single file. Python 3.8+.
