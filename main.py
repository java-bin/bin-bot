from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/kakao-jobs")
def get_latest_jobs(payload: dict = None):
    url = "https://inthiswork.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    items = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # inthiswork.com의 실제 공고 카드 클래스 선택
        cards = soup.select(".wpgb-card")
        
        for card in cards[:5]:  # 상위 5개 공고 추출
            # 공고 제목 및 링크 태그 추출
            title_tag = card.select_one(".wpgb-block-1, .entry-title, h2, h3, a")
            link_tag = card.select_one("a[href]")
            
            if not link_tag:
                continue
                
            title = title_tag.get_text(strip=True) if title_tag else "채용 공고"
            link = link_tag.get("href", url)
            
            # 제목 정리 및 글자 수 제한
            clean_title = title.replace("\n", " ").strip()
            if len(clean_title) > 40:
                clean_title = clean_title[:37] + "..."
                
            items.append({
                "title": clean_title if clean_title else "채용 공고",
                "description": "IN THIS WORK 최신 채용 정보",
                "buttons": [
                    {
                        "action": "webLink",
                        "label": "공고 바로가기 🔗",
                        "webLinkUrl": link
                    }
                ]
            })
            
    except Exception as e:
        print(f"Error fetching data: {e}")

    # 크롤링 실패 시 기본 예외 응답 처리
    if not items:
        items.append({
            "title": "최신 채용 공고 바로가기",
            "description": "아래 버튼을 눌러 인디스워크 웹사이트에서 바로 확인하세요.",
            "buttons": [
                {
                    "action": "webLink",
                    "label": "채용 공고 보기 🔗",
                    "webLinkUrl": "https://inthiswork.com"
                }
            ]
        })

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
