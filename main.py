import os,sys
from . import urlparse
try:
    from dotenv import dotenv_values
    import requests
    
except:
    try:
        os.system("pip install -r requirements.txt")
    except:
        raise Exception("Requirements are not satisfy.")

config = dotenv_values(".env.secret")
thumbnail_url = config["thumbnail_url"]
save = True


# # # # -------------- Supported URL format -----------------
""" https://www.youtube.com/shorts/{VideoID}
    https://www.youtube.com/embed/{VideoID}
    https://www.youtube.com/watch?v={VideoID}
    https://youtu.be/{VideoID}
"""

# # # ------  Fatch Video Id From Youtube URL  --------------
def __get_video_id(url:str)->str:
    # parse_url = urlparse(url)
    parse_url = urlparse.parse_url(url)
    if parse_url.domain in ("www.youtube.com","youtube.com"):
        path = parse_url.path.strip('/').split('/')
        if path[0] == "watch":
            query_url = parse_url.query
            value = query_url.get("v")
            if value:
                return value
            print("Error3")
        elif (path[0] == "shorts" or path[0] == "embed"):
            try:
                return path[1]
            except:
                print("Error4")
        else:
            print("Error2")
    elif parse_url.domain in ("youtu.be","www.youtu.be"):
        path = parse_url.path.strip('/').split('/')
        if path[0]:
            return path[0]
        print("Error5")
    else:
        print("Error1")


# # # --------------- Make a URL for Download Video Thumbnail --------------
def __make_url(videoId:str)->str:
    url = thumbnail_url.replace("videoID",videoId)
    return url


# # # --------- Save The Downloaded File --------------
def __save_file(response:requests.Response,filename:str,path:str,overwrite:bool=False)->bool:
    full_path = os.path.join(path, filename)
    full_path = os.path.normpath(full_path)
    split_file_path = os.path.splitext(full_path)
    full_path = f"{split_file_path[0]}.jpg"
    print(full_path)

    if ((overwrite == False) and (os.path.exists(full_path))):
        for i in range(1,sys.maxsize**10):
            full_path = f"{split_file_path[0]} ({i}).jpg"
            if os.path.exists(full_path) == False:
                break
    
    with open(full_path, 'wb') as f:
        f.write(response.content)
    return True


# # # --------------- Main Function to Download Thumbnail --------------
def download(url,filename="img.jpg",path=".",save=True,overwrite=False):
    id = __get_video_id(url)
    url = __make_url(id)
    response = requests.get(url)
    if response.status_code == 200:
        if save == False:
            return response.content
        return (__save_file(response,filename,path,overwrite))
    else:
        print(f"Error: {response.status_code}")





# # # --------- Test Code ------------


print(download("https://www.youtube.com/watch?v=31k6AtW-b3Y",filename="img"))


url1 = "https://www.youtube.com/watch?v=k5Af8UI1BV8"
url2 = "https://youtu.be/k5Af8UI1BV8"
url3 = "https://youtu.be/k5Af8UI1BV8?t=58"
url4 = "https://www.youtube.com/embed/k5Af8UI1BV8"
url5 = "https://www.youtube.com/shorts/HYYvQOupGSE"
url6 = "https://www.youtube.com/shorts/HYYvQOupGSE?feature=share"
url7 = "https://www.youtube.com/shorts/HYYvQOupGSE?feature=share"
url8 = ""

# print(__get_video_id(url1))
# print(__get_video_id(url2))
# print(__get_video_id(url3))
# print(__get_video_id(url4))
# print(__get_video_id(url5))
# print(__get_video_id(url6))
# print(__get_video_id(url7))