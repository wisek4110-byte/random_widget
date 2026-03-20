import urllib.request
import json
import os

# 깃허브 비밀 설정에서 API 키를 가져옵니다 (안전함)
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = "3296860b8b5e803f9c06c28e343f9076"
URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

req = urllib.request.Request(URL, method="POST")
req.add_header("Authorization", f"Bearer {NOTION_API_KEY}")
req.add_header("Notion-Version", "2022-06-28")
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        results = []
        
        for item in data.get("results", []):
            props = item.get("properties", {})
            
            # 노션 제목 가져오기
            try: title = props.get("이름", {}).get("title", [{}])[0].get("plain_text", "제목 없음")
            except: title = "제목 없음"
            
            # 노션 텍스트 가져오기
            try: text = props.get("텍스트", {}).get("rich_text", [{}])[0].get("plain_text", "")
            except: text = ""
            
            # 노션 이미지 가져오기
            image_url = ""
            try:
                files = props.get("파일", {}).get("files", [])
                if len(files) > 0:
                    image_url = files[0].get("file", {}).get("url") or files[0].get("external", {}).get("url", "")
            except: pass
            
            # 제목이 비어있지 않은 것만 추가
            if title != "제목 없음" or text != "":
                results.append({"title": title, "text": text, "image": image_url})
            
        # 데이터를 data.json 파일로 저장
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print("데이터 업데이트 성공!")
except Exception as e:
    print(f"오류 발생: {e}")