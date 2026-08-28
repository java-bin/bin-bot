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
    }
    
    items = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        visited_links = set()
        a_tags = soup.find_all("a", href=True)
        
        for a in a_tags:
            if len(items) >= 5:
                break
                
            href = a["href"].strip()
            title = a.get_text(strip=True)
            
            # /archives/ 가 포함된 링크 추출 (상대경로 및 절대경로 모두 대응)
            if "/archives/" in href:
                # 풀 URL 주소 완성
                if href.startswith("http"):
                    full_link = href
                else:
                    full_link = f"https://inthiswork.com{href}" if href.startswith("/") else f"https://inthiswork.com/{href}"
                
                # 중복 및 의미없는 짧은 텍스트 제외
                if full_link not in visited_links and len(title) >= 3:
                    visited_links.add(full_link)
                    
                    clean_title = title.replace("\n", " ").strip()
                    if len(clean_title) > 40:
                        clean_title = clean_title[:37] + "..."
                        
                    items.append({
                        "title": clean_title,
                        "description": "IN THIS WORK 최신 채용 정보",
                        "buttons": [
                            {
                                "action": "webLink",
                                "label": "공고 자세히 보기 🔗",
                                "webLinkUrl": full_link
                            }
                        ]
                    })
                    
        print(f"=== 최종 수집된 공고 개수: {len(items)}개 ===")
        for idx, item in enumerate(items, 1):
            print(f"{idx}. {item['title']} -> {item['buttons'][0]['webLinkUrl']}")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

    # 예외 처리
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
