from datetime import date
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from app.database import supabase
from app.services.exhibitions import (get_all_exhibitions,get_exhibition_by_id,create_exhibition,update_exhibition,delete_exhibition,assign_artifact_to_exhibition,remove_artifact_from_exhibition,get_exhibition_artifacts)

router=APIRouter()
templates=Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent/'templates'))
STATUSES=['Planned','Ongoing','Completed','Cancelled']

@router.get('/exhibitions',response_class=HTMLResponse)
async def exhibitions_page(request:Request):
    rows=get_all_exhibitions(); return templates.TemplateResponse(request=request,name='exhibitions.html',context={'exhibitions':rows})

@router.get('/exhibitions/add',response_class=HTMLResponse)
async def exhibition_add_page(request:Request):
    return templates.TemplateResponse(request=request,name='exhibition_form.html',context={'exhibition':{},'statuses':STATUSES})

@router.post('/exhibitions/add')
async def exhibition_add(exhibition_name:str=Form(...),description:str=Form(''),location:str=Form(''),start_date:str=Form(...),end_date:str=Form(...),status:str=Form('Planned')):
    if status not in STATUSES: raise HTTPException(400,'Invalid exhibition status')
    if end_date<=start_date: raise HTTPException(400,'End date must be after start date')
    create_exhibition({'exhibition_name':exhibition_name.strip(),'description':description or None,'location':location or None,'start_date':start_date,'end_date':end_date,'status':status})
    return RedirectResponse('/exhibitions',303)

@router.get('/exhibitions/{exhibition_id}',response_class=HTMLResponse)
async def exhibition_page(request:Request,exhibition_id:str):
    item=get_exhibition_by_id(exhibition_id)
    if not item: raise HTTPException(404,'Exhibition not found')
    assigned=get_exhibition_artifacts(exhibition_id)
    artifacts=supabase.table('artifacts').select('artifact_id,title').order('title').execute().data or []
    linked={r.get('artifact_id') for r in assigned}; available=[a for a in artifacts if a['artifact_id'] not in linked]
    return templates.TemplateResponse(request=request,name='exhibition_details.html',context={'exhibition':item,'assigned':assigned,'available':available})

@router.get('/exhibitions/{exhibition_id}/edit',response_class=HTMLResponse)
async def exhibition_edit_page(request:Request,exhibition_id:str):
    item=get_exhibition_by_id(exhibition_id)
    if not item: raise HTTPException(404,'Exhibition not found')
    return templates.TemplateResponse(request=request,name='exhibition_form.html',context={'exhibition':item,'statuses':STATUSES})

@router.post('/exhibitions/{exhibition_id}/edit')
async def exhibition_edit(exhibition_id:str,exhibition_name:str=Form(...),description:str=Form(''),location:str=Form(''),start_date:str=Form(...),end_date:str=Form(...),status:str=Form('Planned')):
    if status not in STATUSES or end_date<=start_date: raise HTTPException(400,'Check exhibition status and date range')
    if not update_exhibition(exhibition_id,{'exhibition_name':exhibition_name.strip(),'description':description or None,'location':location or None,'start_date':start_date,'end_date':end_date,'status':status}): raise HTTPException(404,'Exhibition not found')
    return RedirectResponse(f'/exhibitions/{exhibition_id}',303)

@router.post('/exhibitions/{exhibition_id}/delete')
async def exhibition_delete_page(exhibition_id:str):
    # Remove only relationship rows; artifact records remain untouched.
    supabase.table('exhibition_artifacts').delete().eq('exhibition_id', exhibition_id).execute()
    delete_exhibition(exhibition_id)
    return RedirectResponse('/exhibitions',303)

@router.post('/exhibitions/{exhibition_id}/artifacts')
async def exhibition_assign(exhibition_id:str,artifact_id:str=Form(...)):
    existing=supabase.table('exhibition_artifacts').select('artifact_id').eq('exhibition_id',exhibition_id).eq('artifact_id',artifact_id).execute().data or []
    if not existing: assign_artifact_to_exhibition(exhibition_id,artifact_id)
    return RedirectResponse(f'/exhibitions/{exhibition_id}',303)

@router.post('/exhibitions/{exhibition_id}/artifacts/{artifact_id}/remove')
async def exhibition_unassign(exhibition_id:str,artifact_id:str):
    remove_artifact_from_exhibition(exhibition_id,artifact_id); return RedirectResponse(f'/exhibitions/{exhibition_id}',303)

# Existing JSON API retained under /api/exhibitions.
api_router=APIRouter(prefix='/api/exhibitions',tags=['Exhibitions'])
class ExhibitionCreate(BaseModel):
    exhibition_name:str=Field(min_length=1,max_length=200); description:str|None=None; location:str|None=None; start_date:date; end_date:date; status:str='Planned'
class ArtifactAssignment(BaseModel): artifact_id:UUID
@api_router.get('/')
def api_list_exhibitions(): return get_all_exhibitions()
@api_router.get('/{exhibition_id}')
def api_exhibition_details(exhibition_id:str):
    item=get_exhibition_by_id(exhibition_id)
    if item is None: raise HTTPException(404,'Exhibition not found')
    return item
@api_router.post('/',status_code=201)
def api_add_exhibition(exhibition:ExhibitionCreate):
    if exhibition.status not in STATUSES or exhibition.end_date<=exhibition.start_date: raise HTTPException(400,'Invalid status or date range')
    return create_exhibition(exhibition.model_dump(mode='json'))
@api_router.put('/{exhibition_id}')
def api_edit_exhibition(exhibition_id:str,exhibition:ExhibitionCreate):
    if exhibition.status not in STATUSES or exhibition.end_date<=exhibition.start_date: raise HTTPException(400,'Invalid status or date range')
    result=update_exhibition(exhibition_id,exhibition.model_dump(mode='json'))
    if result is None: raise HTTPException(404,'Exhibition not found')
    return result
@api_router.delete('/{exhibition_id}')
def api_delete_exhibition(exhibition_id:str):
    supabase.table('exhibition_artifacts').delete().eq('exhibition_id', exhibition_id).execute()
    if not delete_exhibition(exhibition_id): raise HTTPException(404,'Exhibition not found')
    return {'message':'Exhibition deleted successfully'}
@api_router.post('/{exhibition_id}/artifacts',status_code=201)
def api_assign_artifact(exhibition_id:UUID,assignment:ArtifactAssignment):
    eid=str(exhibition_id); aid=str(assignment.artifact_id)
    exists=supabase.table('exhibition_artifacts').select('artifact_id').eq('exhibition_id',eid).eq('artifact_id',aid).execute().data or []
    return exists[0] if exists else assign_artifact_to_exhibition(eid,aid)
@api_router.get('/{exhibition_id}/artifacts')
def api_list_exhibition_artifacts(exhibition_id:UUID): return get_exhibition_artifacts(str(exhibition_id))
@api_router.delete('/{exhibition_id}/artifacts/{artifact_id}')
def api_unassign_artifact(exhibition_id:UUID,artifact_id:UUID):
    if not remove_artifact_from_exhibition(str(exhibition_id),str(artifact_id)): raise HTTPException(404,'Assignment not found')
    return {'message':'Artifact removed from exhibition successfully'}
