from pathlib import Path
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import supabase

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get('/institutions', response_class=HTMLResponse)
async def institutions_page(request: Request, q: str = ''):
    rows = supabase.table('institutions').select('*').order('institution_name').execute().data or []
    if q.strip():
        term=q.strip().lower(); rows=[r for r in rows if term in (r.get('institution_name') or '').lower() or term in (r.get('email') or '').lower()]
    return templates.TemplateResponse(request=request, name='institutions.html', context={'institutions':rows,'q':q})

@router.get('/institutions/{institution_id}', response_class=HTMLResponse)
async def institution_detail_page(request: Request, institution_id: str):
    found = supabase.table('institutions').select('*').eq('institution_id', institution_id).limit(1).execute().data or []
    if not found: raise HTTPException(404, 'Institution not found')
    loans = supabase.table('loans').select('*, artifacts(title)').eq('institution_id', institution_id).order('loan_date', desc=True).execute().data or []
    return templates.TemplateResponse(request=request, name='institution_details.html', context={'institution': found[0], 'loans': loans})

@router.get('/institutions/add', response_class=HTMLResponse)
async def institution_add_page(request: Request):
    return templates.TemplateResponse(request=request, name='institution_form.html', context={'institution':{}})

@router.post('/institutions/add')
async def institution_add(institution_name: str=Form(...), contact_person: str=Form(''), email: str=Form(''), phone: str=Form(''), address: str=Form('')):
    supabase.table('institutions').insert({'institution_name':institution_name.strip(),'contact_person':contact_person or None,'email':email or None,'phone':phone or None,'address':address or None}).execute()
    return RedirectResponse('/institutions',303)

@router.get('/institutions/{institution_id}/edit', response_class=HTMLResponse)
async def institution_edit_page(request: Request, institution_id: str):
    result=supabase.table('institutions').select('*').eq('institution_id',institution_id).limit(1).execute().data or []
    if not result: raise HTTPException(404,'Institution not found')
    return templates.TemplateResponse(request=request,name='institution_form.html',context={'institution':result[0]})

@router.post('/institutions/{institution_id}/edit')
async def institution_edit(institution_id: str, institution_name: str=Form(...), contact_person: str=Form(''), email: str=Form(''), phone: str=Form(''), address: str=Form('')):
    supabase.table('institutions').update({'institution_name':institution_name.strip(),'contact_person':contact_person or None,'email':email or None,'phone':phone or None,'address':address or None}).eq('institution_id',institution_id).execute()
    return RedirectResponse('/institutions',303)

@router.post('/institutions/{institution_id}/delete')
async def institution_delete(institution_id: str):
    # Foreign keys protect institutions referenced by loan history.
    supabase.table('institutions').delete().eq('institution_id',institution_id).execute()
    return RedirectResponse('/institutions',303)
