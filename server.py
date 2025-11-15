from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from typing import List, Annotated
import qrcode

root_path = os.getcwd()
abs_path =  os.path.join(root_path,'all_file')
upload_path = os.path.join(root_path,'all_file')
varlist = ['folder','image','audio','video','pdf','file']
password = '123'

security = HTTPBasic()

def retlist(path="",sh=False):
    all_list = []
    for i in range(0,7):
        all_list.append([])
    new_path = os.path.join(abs_path,path)    
    files0 = os.listdir(os.path.join(abs_path,path))
    files=[]
    for ff in files0:
        if sh==False:
            if not ff.startswith('.'):
                files.append(ff)
        else:
            files.append(ff)
    files.sort()
    for f in files:
        if os.path.isdir(os.path.join(new_path,f)):                 
            all_list[0].append(f)            
        if os.path.isfile(os.path.join(new_path,f)):
            filetype = os.path.splitext(os.path.join(new_path,f))
            if  [x for x in ['jpg','png','bmp','jpeg','gif'] if x in filetype[1]]:
                all_list[1].append(f)
            elif  [x for x in ['mp3','wav'] if x in filetype[1]]:
                all_list[2].append(f)
            elif  [x for x in ['mp4','mkv','mpg','mpeg','avi'] if x in filetype[1]]:
                all_list[3].append(f)
            elif  [x for x in ['pdf'] if x in filetype[1]]:
                all_list[4].append(f)
            else:
                all_list[5].append(f)
    return all_list



# Initialize FastAPI app
app = FastAPI()

# Mount static files (similar to Flask's static_folder)
app.mount("/static", StaticFiles(directory=os.path.join(root_path,'static')), name="static")

# Setup templates (similar to Flask's template_folder)
templates = Jinja2Templates(directory=os.path.join(root_path,'templates'))

@app.get("/")
async def index(request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    delitem = 0
    if credentials.username == 'epfa' and credentials.password == password:
        delitem=1
    if delitem==1:
            lst = retlist(sh=True)
    else:
            lst = retlist()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "path": "",
        "all_list": lst,
        "varlist": varlist,
        "delitem": delitem
    })

# Uncomment if you need this functionality
'''
import pyotp, glob
@app.get("/rm/{code}/{path}")
async def rm_file(code: str, path: str):
    otp_chk = pyotp.TOTP('EBRAHIMARSHAGOOGLE')
    if otp_chk.now() == code:
        files = glob.glob(f'{abs_path}/{path}')
        for file in files:
            os.remove(file)
    return RedirectResponse(url="/")
'''

@app.get("/del/{path:path}")
async def del_item(path: str, request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username == 'epfa' and credentials.password == password:
        os.remove(f'{abs_path}/{path}')
    return RedirectResponse(url="/")

@app.get("/nosh/{path:path}")
async def nosh_item(path: str, request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username == 'epfa' and credentials.password == password:
        split_text =  path.split('/')
        if split_text[-1][0]!='.':
            split_text[-1] = '.' + split_text[-1]
        else:
            split_text[-1] =  split_text[-1][1:]
        st = '/'.join(split_text)
        os.rename(f'{abs_path}/{path}',f'{abs_path}/{st}')        
    return RedirectResponse(url="/")

@app.get("/qr/{path:path}")
def qrcod(path: str, request: Request):
    qp = request.query_params
    txt = path
    for i ,(k, v) in enumerate(qp.items()):
        if i==0:
            txt += f'?{k}={v}'
        if i>0:
            txt += f'&{k}={v}'
    img = qrcode.make(txt)
    full_path = os.path.join(root_path, 'qr.png')
    img.save(full_path)
    return FileResponse(full_path)

@app.get("/qr")
async def qr():
    return HTMLResponse('''
        <!DOCTYPE html>
        <html>
        <body>
        <h2>Enter String for Qr code</h2>
        <form action="/qrres"  method="POST">
          <label for="txt">Enter your text: </label>
          <input type="text" id="txt" name="txt" value="" autofocus >
          <input type="submit" value="Generate Qr Code">
        </form>
        </body>
        </html>
    ''')

@app.post("/qrres")
async def qrres(txt: Annotated[str, Form()]):
    img = qrcode.make(txt)
    full_path = os.path.join(root_path, 'qr.png')
    img.save(full_path)
    return FileResponse(full_path)

@app.get("/{path:path}", response_class=HTMLResponse)
async def dir_listing(path: str, request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    full_path = os.path.join(abs_path, path)
    delitem = 0
    if credentials.username == 'epfa' and credentials.password == password:
        delitem=1    
    if os.path.isdir(full_path):
        if delitem==1:
            lst = retlist(path,True)
        else:
            lst = retlist(path)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "path": path,
            "all_list": lst,
            "varlist": varlist,
            "delitem": delitem
        })
    else:
        if os.path.exists(full_path):
            return FileResponse(full_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")

@app.get("/mkdir/{path:path}")
def mkdir(path: str, request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username == 'epfa' and credentials.password == password:
        os.mkdir(f"{abs_path}/{path}")
    return RedirectResponse(url=f"/{path}")

@app.post("/uploadfiles/{path:path}")
async def upload_file_path(path: str, file: List[UploadFile] = File(...)):
    for fi in file:
        file_path0 = os.path.join(abs_path , path)
        file_path = os.path.join(file_path0 , fi.filename)
        with open(file_path, "wb") as f:
            f.write(await fi.read())
    return RedirectResponse(url=f"/{path}")


@app.post("/uploadfiles")
async def upload_file(file: List[UploadFile] = File(...)):
    for fi in file:
        file_path = os.path.join(abs_path , fi.filename)
        with open(file_path, "wb") as f:
            f.write(await fi.read())
    return RedirectResponse(url="/")

#import uvicorn
#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)

