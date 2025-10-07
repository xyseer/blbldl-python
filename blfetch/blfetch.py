import requests
import bs4
import json
info_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'sec-fetch-dest': 'document',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate',
        'upgrade-insecure-requests': "1",
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'Cookie':"",
}
result_list=[]
try:
    info_headers['Cookie'] = open('cookie', 'r').readline()
except Exception as e:
    print('Cookie loads error')


def ret_url(mid,pn=0):
    return f"https://api.bilibili.com/x/series/recArchivesByKeywords?mid={mid}&order=pubdate&ps=0&pn={pn}&keywords="

if __name__=="__main__":
    r=requests.get(ret_url(654552,596),headers=info_headers)
    jsondoc=r.text
    jsondic=json.loads(jsondoc)
    items=jsondic['data']['archives']
    items_sorted = sorted(items, key=lambda x: x['duration'], reverse=True)
    print(len(items_sorted))
    for i in items_sorted:
        result_list.append((i.get("bvid",0),i.get('title','')))

    # with open("bldl_script.cmd","w") as w:
    #     for j in result_list:
    #         if j!=0:
    #             w.write("python3 blbldl.py "+str(j[0])+" ass+\n")

    with open("bldl_name_id_to_filter.json", "w") as w:
        json.dump(result_list,w,ensure_ascii=False)

