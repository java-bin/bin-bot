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
        
        # inthiswork.com 메인 페이지의 글 링크 항목 추출
        # 보통 h2/h3 태그 내의 a 태그 또는 article 태그 내의 a 태그에 링크가 있습니다.
        articles = soup.find_all("article")
        
        for article in articles[:5]:  # 상위 5개 추출
            a_tag = article.find("a")
            if not a_tag:
                continue
                
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", url)
            
            # 제목 길이 제한 및 정리
            if len(title) > 40:
                title = title[:37] + "..."
                
            items.append({
                "title": title if title else "채용 공고",
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

    # 크롤링 실패나 개수 부족 시 기본 예외 응답 처리
    if not items:
        items.append({
            "title": "최신 채용 공고를 불러왔습니다.",
            "description": "아래 버튼을 눌러 웹사이트에서 바로 확인하세요.",
            "buttons": [
                {
                    "action": "webLink",
                    "label": "채용 공고 바로가기 🔗",
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
