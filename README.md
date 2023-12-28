# jager
jager is accountable, privacy-preserving, fast phone call traceback project. It requires cooperation between mutliple authorities and phone companies to trace phone calls.

## Useful Commands
- Check table sizes in clickhouse
```
sql
SELECT table, formatReadableSize(size) as size, rows, days, formatReadableSize(avgDaySize) as avgDaySize FROM (
    SELECT
        table,
        sum(bytes) AS size,
        sum(rows) AS rows,
        min(min_date) AS min_date,
        max(max_date) AS max_date,
        (max_date - min_date) AS days,
        size / (max_date - min_date) AS avgDaySize
    FROM system.parts
    WHERE active
    GROUP BY table
    ORDER BY rows DESC
);
```

## Resources
- [Robocall Mitigation Database](https://fccprod.servicenowservices.com/rmd?id=rmd_welcome)
