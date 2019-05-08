import os
import re
import sys
from jinja2 import Template

path = "app"
files = []

def extract_brief(info):
    brief = re.findall(r"@brief(.*?)##\n", info, re.S)
    brief = ' '.join(brief[0].split())
    return brief

def extract_params(info):

    params_arr = []
    params = re.findall(r"(?<=@param).*?(?=@emit|@param|@socketio)", info, re.S)

    for i in range(len(params)):
        params[i]  = re.sub(' +', ' ', params[i]).lstrip()
        params[i] = params[i].replace('#', '')

        param_name = params[i].split()[0]
        param_desc = params[i].lstrip(param_name)

        if "!" not in param_name:
            continue
        
        param_name = param_name.strip("!")

        param_desc_attrs = re.findall(r"([\+|-].*):(.*\[.*\])(.*)", param_desc)
        param_attrs = []
        
        for param_attr in param_desc_attrs:
            param_attrs.append({
                "name": param_attr[0],
                "type": param_attr[1].strip(),
                "description": param_attr[2].strip()
            })
        
        param_desc = re.findall(r"^(?:.+[\n\r])+", param_desc, re.M)
        param_desc = param_desc[0].strip()
        param_desc = param_desc.replace("\n", "")
        params_arr.append({
            "name": param_name,
            "description": param_desc,
            "attributes": param_attrs
        })
    
    return params_arr

def get_functions(path):
    functions = []

    for (dirpath, _, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith('controllers.py'):
                files.append(os.sep.join([dirpath, filename]))
    
    textfile = open(files[0], 'r')
    filetext = textfile.read()
    textfile.close()
    f_headers = re.findall(r"(## @brief(.|\n)*?@socketio.on\('(.*?)'\))", filetext)

    for f_header in f_headers:
        functions.append({
            "endpoint_name": f_header[2],
            "description": extract_brief(f_header[0]),
            "params": extract_params(f_header[0])
        })
    
    with open('index.html') as file_:
        template = Template(file_.read())
    print(template.render(endpoints = functions))
    

def main():
    args = sys.argv
    path = args[1].replace("-path=", "")
    f = get_functions(path)
    

if __name__ == "__main__":
    main()
