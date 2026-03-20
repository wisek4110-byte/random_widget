import urllib.request
import json
import os
import re

# 깃허브 비밀 설정에서 API 키를 가져옵니다 (안전함)
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = "3296860b8b5e803f9c06c28e343f9076"
URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

def get_notion_data():
    req = urllib.request.Request(URL, method="POST")
    req.add_header("Authorization", f"Bearer {NOTION_API_KEY}")
    req.add_header("Notion-Version", "2022-06-28")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"노션 API 호출 오류: {e}")
        return None

def convert_to_notion_thumbnail(original_url):
    # 노션 자체 파일 포맷팅 규칙을 이용해 썸네일 URL로 변환 시도 (실험적 기능)
    if not original_url or "secure.notion-static.com" not in original_url:
        return original_url
        
    try:
        # URL에서 이미지 ID 추출
        match = re.search(r'secure.notion-static.com/([^/]+)/', original_url)
        if match:
            image_id = match.group(1)
            # 노션 이미지 렌더링 서버 주소로 변환 (너비 600px로 제한)
            encoded_url = urllib.parse.quote(original_url, safe='')
            thumbnail_url = f"https://www.notion.so/image/{encoded_url}?table=block&id={image_id}&width=600&cache=v2"
            return thumbnail_url
    except:
        pass
    return original_url # 변환 실패 시 원본 반환

data = get_notion_data()
if data:
    results = []
    for item in data.get("results", []):
        props = item.get("properties", {})
        
        # 노션 제목 가져오기
        try: title = props.get("이름", {}).get("title", [{}])[0].get("plain_text", "제목 없음")
        except: title = "제목 없음"
        
        # 노션 텍스트 가져오기
        try: text = props.get("텍스트", {}).get("rich_text", [{}])[0].get("plain_text", "")
        except: text = ""
        
        # 노션 이미지 가져오기 및 썸네일 변환
        image_url = ""
        try:
            files = props.get("파일", {}).get("files", [])
            if len(files) > 0:
                original_url = files[0].get("file", {}).get("url") or files[0].get("external", {}).get("url", "")
                # 원본 대신 썸네일 주소로 변환 (속도 개선 핵심)
                image_url = convert_to_notion_thumbnail(original_url)
        except: pass
        
        if title != "제목 없음" or text != "":
            results.append({"title": title, "text": text, "image": image_url})
            
    # 데이터를 data.json 파일로 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print("데이터 업데이트 성공! (이미지 썸네일 변환 적용)")
