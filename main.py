from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import re

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
        
        # 방식 1: article 태그의 id="post-XXXXXX" 또는 class에서 게시글 ID 추출
        articles = soup.find_all(re.compile("article|div"), id=re.compile(r"post-\d+"))
        
        for article in articles:
            if len(items) >= 5:
                break
                
            # post-392039 형태에서 숫자 ID 추출
            post_id_match = re.search(r"post-(\d+)", article.get("id", ""))
            if not post_id_match:
                continue
                
            post_id = post_id_match.group(1)
            full_link = f"https://inthiswork.com/archives/{post_id}"
            
            if full_link in visited_links:
                continue
                
            # 해당 글 카드 안의 제목 텍스트 추출
            title_tag = article.find(re.compile("h1|h2|h3|h4|a"))
            title = title_tag.get_text(strip=True) if title_tag else "채용 공고"
            
            visited_links.add(full_link)
            
            clean_title = title.replace("\n", " ").strip()
            if len(clean_title) > 40:
                clean_title = clean_title[:37] + "..."
                
            items.append({
                "title": clean_title if clean_title else "IN THIS WORK 채용공고",
                "description": "IN THIS WORK 실시간 채용 정보",
                "buttons": [
                    {
                        "action": "webLink",
                        "label": "공고 자세히 보기 🔗",
                        "webLinkUrl": full_link
                    }
                ]
            })

        # 방식 2: 만약 post-ID 구조를 못 찾았을 경우 전체 href 중 숫자 포함 링크 탐색
        if len(items) < 5:
            for a in soup.find_all("a", href=True):
                if len(items) >= 5:
                    break
                href = a["href"].strip()
                title = a.get_text(strip=True)
                
                # archives/숫자 또는 ?p=숫자 패턴 검색
                match = re.search(r"(/archives/|\?p=)(\d+)", href)
                if match:
                    post_id = match.group(2)
                    full_link = f"https://inthiswork.com/archives/{post_id}"
                    
                    if full_link not in visited_links and len(title) >= 3:
                        visited_links.add(full_link)
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
                                    "webLinkUrl": full_link
                                }
                            ]
                        })

        print(f"=== 최종 수집된 공고 개수: {len(items)}개 ===")
        for idx, item in enumerate(items, 1):
            print(f"{idx}. {item['title']} -> {item['buttons'][0]['webLinkUrl']}")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

    # 비상 예외 응답
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
