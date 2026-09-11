import requests
from bs4 import BeautifulSoup
import pickle
import time

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"}

def InnerUrl(id, cpi):
    return f"https://sldict.korean.go.kr/front/sign/signContentsView.do?current_pos_index={cpi}&origin_no={id}&searchWay=&top_category=CTE&category=&detailCategory=&searchKeyword=&pageIndex=2&pageJumpIndex="


def OuterUrl(page):
    return f"https://sldict.korean.go.kr/front/sign/signList.do?current_pos_index=&origin_no=0&searchWay=&top_category=&category=CTE001&detailCategory=&searchKeyword=&pageIndex={page}&pageJumpIndex="


def generate_soup(url,header,params=None):
    resp = requests.get(url,headers=header,params=params)
    soup = BeautifulSoup(resp.content, "html.parser")
    return soup

def GetSignName(id, cpi):
    soup = generate_soup(InnerUrl(id,cpi),headers)
    dd = soup.select('.content_view_dis')[1].select_one("dd")
    if dd is not None:
        return str(dd.text).strip().split(",")[0]
    return None

def GetVideoUrl(id, cpi):
    nheaders = headers.copy()
    nheaders["Referer"] = InnerUrl(id, cpi)
    params = {"origin_no":id,"current_pos_index":cpi}
    soup = generate_soup("https://sldict.korean.go.kr/front/sign/include/controlVideoSpeed.do", nheaders,params)
    srcs = soup.select("source")
    for src_o in srcs:
        src = str(src_o.get("src"))
        if not src.endswith("mp4"):
            continue
        src = src.replace("http","https").replace("320X240","700X466")
        return src
    return None

def GetVideosFromDownload():
    vids = {}
    error_count = 0
    for p in range(100):
        try:
            soup = generate_soup(OuterUrl(p+1),headers)
            spans = soup.select(".tit")
            for span in spans:
                a = span.find("a")
                if a is None:
                    continue
                href = str(a.get("href"))
                props = href.split("(")[1].split(")")[0].split(",")
                id = props[0].replace("'", "")
                cpi = props[1].replace("'", "").replace(" ", "")
                sign_name = GetSignName(id,cpi)
                vurl = GetVideoUrl(id, cpi)

                if vurl is not None:
                    name = sign_name if sign_name is not None else id
                    vid = requests.get(vurl,headers=headers).content
                    vids[name] = vid
                    #open(f"video_tests/{name}.mp4", "wb").write(vid)

            print(f"current page: {p+1}")
        except Exception as e:
            print(f"Error occured ({error_count}/3): {e}")
            error_count += 1
            if error_count > 3:
                print("Too many errors, exiting...")
                break
            continue
    return vids

def GetVideosFromFile():
    vids = None
    try:
        with open("./data/vid_data.pkl", "rb") as f:
            vids = pickle.load(f)
    except Exception as e:
        print(f"Error while loading: {e}")
    return vids

if __name__ == "__main__":
    if (input("wanna rewrite the video data file? (y/n) > ").lower()=="y"):
        start_time = time.time()
        vids = GetVideosFromDownload()
        with open("../data/vid_data.pkl", "wb") as f:
            pickle.dump(vids, f)
        print("ended, total time spent: ", time.time()-start_time)
    else:
        start_time = time.time()
        vids = GetVideosFromFile()
        print("loaded, total time spent: ", time.time()-start_time)