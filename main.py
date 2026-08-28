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
    
    # 카카오톡에 보여줄 카드 목록
    items = []
    
    # 최신 공고 상위 5개 가져오기
    for entry in feed.entries[:5]:
        title = entry.get('title', '채용 공고')
        link = entry.get('link', 'https://inthiswork.com')
        
        # 각 공고를 텍스트 카드(TextCard) 형태로 구성
        card = {
            "title": title[:50],  # 제목 글자수 제한 예방
            "description": "IN THIS WORK 실시간 채용 정보",
            "buttons": [
                {
                    "action": "webLink",
                    "label": "공고 자세히 보기 🔗",
                    "webLinkUrl": link
                }
            ]
        }
        items.append(card)
    
    # 여러 카드를 Carousel(캐러셀) 형태로 응답
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "carousel": {
                        "type": "textCard",
                        "items": items
                    }
                }
            ]
        }
    }
