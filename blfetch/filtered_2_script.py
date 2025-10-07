import json
if __name__=="__main__":
    result_list =[]
    with open("bldl_name_id_to_filter.json", "r") as w:
        result_list=json.load(w)
    with open("bldl_script.cmd", "w") as w:
        for j in result_list:
            if j!=0:
                w.write("python3 blbldl.py "+str(j[0])+" ass+\n")
