from fastapi import FastAPI
import feedparser

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/kakao-jobs")
def get_latest_jobs(payload: dict):
    feed_url = "https://inthiswork.com/feed"
    feed = feedparser.parse(feed_url)
    
    job_items = []
    for entry in feed.entries[:3]:
        title = entry.title
        link = entry.link
        job_items.append(f"📌 {title}\n🔗 {link}")
    
    response_text = "📢 [IN THIS WORK] 최신 채용 공고입니다:\n\n" + "\n\n".join(job_items)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }