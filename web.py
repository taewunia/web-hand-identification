import requests
from bs4 import BeautifulSoup
from io import BytesIO


def InnerUrl(id, cpi):
    return f"https://sldict.korean.go.kr/front/sign/signContentsView.do?current_pos_index={cpi}&origin_no={id}&searchWay=&top_category=CTE&category=&detailCategory=&searchKeyword=&pageIndex=2&pageJumpIndex="


def OuterUrl(page):
    return f"https://sldict.korean.go.kr/front/sign/signList.do?current_pos_index=&origin_no=0&searchWay=&top_category=CTE&category=&detailCategory=&searchKeyword=&pageIndex={page}&pageJumpIndex="


def generate_soup(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup


def GetVideoUrl(id, cpi):
    soup = generate_soup(InnerUrl(id, cpi))
    vids = soup.select("#html5Video")
    print(InnerUrl(id, cpi))
    print(soup)
    f = open("a.html", "w")
    f.write(str(soup))
    for vid in vids:
        for src_o in vid.select("source"):
            src = str(src_o.get("src"))
            if not src.endswith("mp4"):
                break
            return src
    return None


soup = generate_soup(OuterUrl(1))
spans = soup.select(".tit")
for span in spans:
    a = span.find("a")
    if a is None:
        continue
    href = str(a.get("href"))
    props = href.split("(")[1].split(")")[0].split(",")
    id = props[0].replace("'", "")
    cpi = props[1].replace("'", "").replace(" ", "")
    vurl = GetVideoUrl(id, cpi)

    if vurl is not None:
        print(vurl)
    break
