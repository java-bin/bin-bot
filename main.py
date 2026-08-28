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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    
    items = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # inthiswork.com 페이지 내부의 모든 <a> 태그 탐색
        a_tags = soup.find_all("a", href=True)
        visited_links = set()
        
        for a in a_tags:
            if len(items) >= 5:
                break
                
            link = a["href"].strip()
            title = a.get_text(strip=True)
            
            # /archives/ 가 들어간 링크가 실제 채용 공고 포스팅 주소입니다.
            if "/archives/" in link or "?p=" in link:
                if link not in visited_links and len(title) > 3:
                    visited_links.add(link)
                    
                    # 제목 정제 및 길이고정
                    clean_title = title.replace("\n", " ").strip()
                    if len(clean_title) > 40:
                        clean_title = clean_title[:37] + "..."
                        
                    items.append({
                        "title": clean_title,
                        "description": "IN THIS WORK 실시간 채용 정보",
                        "buttons": [
                            {
                                "action": "webLink",
                                "label": "공고 자세히 보기 🔗",
                                "webLinkUrl": link
                            }
                        ]
                    })
                    
        # Render 대시보드 Logs에서 수집 결과를 바로 확인하기 위한 디버그 출력
        print(f"=== 수집된 공고 개수: {len(items)}개 ===")
        for idx, item in enumerate(items, 1):
            print(f"{idx}. {item['title']} ({item['buttons'][0]['webLinkUrl']})")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

    # 공고를 하나도 찾지 못했을 때 예외 비상 메시지
    if not items:
        items.append({
            "title": "IN THIS WORK 최신 채용 공고",
            "description": "아래 버튼을 눌러 웹사이트에서 실시간 공고를 확인하세요.",
            "buttons": [
                {
                    "action": "webLink",
                    "label": "공고 목록 전체보기 🔗",
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
