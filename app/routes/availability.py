from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.services.availability import get_artifact_availability

router=APIRouter()
templates=Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent/'templates'))

@router.get('/availability',name='availability_page')
async def availability_page(request:Request,q:str=''):
    items=get_artifact_availability(q)
    return templates.TemplateResponse(request=request,name='availability.html',context={'items':items,'q':q})
