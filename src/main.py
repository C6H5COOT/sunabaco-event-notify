from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

now = datetime.now(JST)
print("✅ GitHub Actions で Python が動きました！")
print("JST now:", now.isoformat())
