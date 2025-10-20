from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from typing import List, Annotated
import qrcode

root_path = '/home/epfa/epfs7'#os.getcwd()
abs_path =  '/home/epfa/epfs7/all_file'
upload_path = os.path.join(root_path,'all_file')
varlist = ['folder','image','audio','video','pdf','file']

security = HTTPBasic()

def retlist(path=""):
    all_list = []
    for i in range(0,7):
        all_list.append([])
    new_path = os.path.join(abs_path,path)
    files = os.listdir(os.path.join(abs_path,path))
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
    lst = retlist()
    delitem = 0
    if credentials.username == 'epfa' and credentials.password == 'e734432e7':
        delitem=1
    return templates.TemplateResponse("index.html", {
        "request": request,
        "path": "",
        "all_list": lst,
        "varlist": varlist,
        "delitem": delitem
    })

@app.get("/rm/{code}/{path}")
async def rm_file(code: str, path: str):
    otp_chk = pyotp.TOTP('EBRAHIMARSHAGOOGLE')
    if otp_chk.now() == code:
        files = glob.glob(f'{abs_path}/{path}')
        for file in files:
            os.remove(file)
    return RedirectResponse(url="/")

@app.get("/del/{path:path}")
async def del_item(path: str, request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username == 'epfa' and credentials.password == 'e734432e7':
        os.remove(f'{abs_path}/{path}')
    return RedirectResponse(url="/")

@app.get("/qr/{path:path}")
def qrcod(path: str, , request: Request):
    img = qrcode.make(f'{path}')
    full_path = os.path.join(root_path, 'qr.png')
    img.save(full_path)
    return FileResponse(full_path)


@app.get("/{path:path}", response_class=HTMLResponse)
async def dir_listing(path: str, request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    full_path = os.path.join(abs_path, path)
    delitem = 0
    if credentials.username == 'epfa' and credentials.password == 'e734432e7':
        delitem=1

    if os.path.isdir(full_path):
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


# Uncomment if you need this functionality
import pyotp, glob

@app.post("/uploadfiles")
async def upload_image(file: List[UploadFile] = File(...)):
    for fi in file:
        file_path = os.path.join(abs_path, fi.filename)
        with open(file_path, "wb") as f:
            f.write(await fi.read())
    return RedirectResponse(url="/", status_code=303)

#import uvicorn
#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)

