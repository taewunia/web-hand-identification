import requests
from bs4 import BeautifulSoup

def InnerUrl(id, cpi):
    return F"https://sldict.korean.go.kr/front/sign/signContentsView.do?current_pos_index={cpi}&origin_no={id}&searchWay=&top_category=&category=CTE001&detailCategory=&searchKeyword=&pageIndex=1&pageJumpIndex="

def OuterUrl(page):
    return F"https://sldict.korean.go.kr/front/sign/signList.do?current_pos_index=9&origin_no=7664&searchWay=&top_category=&category=CTE001&detailCategory=&searchKeyword=&pageIndex={page}&pageJumpIndex="

def generate_soup(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content,'html.parser')
    return soup

def GetVideo(id, cpi):
    soup = generate_soup(InnerUrl(id,cpi))


soup = generate_soup(OuterUrl(1))
spans = soup.select('.tit')
for span in spans:
    href = span.find('a').get('href')
    props = href.split("(")[1].split(")")[0].split(",")
    id = props[0].replace("'", "")
    cpi = props[1].replace("'", "").replace(" ","")
    GetVideo(id, cpi)
    break