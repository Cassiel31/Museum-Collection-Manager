from pathlib import Path
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import supabase
from app.services.loans import get_all_loans, artifact_has_open_loan, create_loan, update_loan, delete_loan

router=APIRouter()
templates=Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent/'templates'))
STATUSES=['Pending','Active','Returned','Cancelled']

def _choices():
    artifacts=supabase.table('artifacts').select('artifact_id,title').order('title').execute().data or []
    institutions=supabase.table('institutions').select('institution_id,institution_name').order('institution_name').execute().data or []
    return artifacts,institutions

@router.get('/loans',response_class=HTMLResponse)
async def loans_page(request:Request,q:str=''):
    rows=get_all_loans()
    if q.strip():
        t=q.strip().lower(); rows=[r for r in rows if t in (r.get('status') or '').lower() or t in ((r.get('artifacts') or {}).get('title') or '').lower() or t in ((r.get('institutions') or {}).get('institution_name') or '').lower()]
    return templates.TemplateResponse(request=request,name='loans.html',context={'loans':rows,'q':q})

@router.get('/loans/add',response_class=HTMLResponse)
async def loan_add_page(request:Request):
    a,i=_choices(); return templates.TemplateResponse(request=request,name='loan_form.html',context={'loan':{},'artifacts':a,'institutions':i,'statuses':STATUSES})

@router.post('/loans/add')
async def loan_add(artifact_id:str=Form(...),institution_id:str=Form(...),loan_date:str=Form(...),expected_return_date:str=Form(...),actual_return_date:str=Form(''),status:str=Form('Pending'),notes:str=Form('')):
    if status not in STATUSES: raise HTTPException(400,'Invalid loan status')
    # Prevent a second pending/active loan for the same artifact.
    if artifact_has_open_loan(artifact_id): raise HTTPException(409,'This artifact already has a pending or active loan.')
    create_loan({'artifact_id':artifact_id,'institution_id':institution_id,'loan_date':loan_date,'expected_return_date':expected_return_date,'actual_return_date':actual_return_date or None,'status':status,'notes':notes or None})
    return RedirectResponse('/loans',303)

@router.get('/loans/{loan_id}/edit',response_class=HTMLResponse)
async def loan_edit_page(request:Request,loan_id:str):
    found=supabase.table('loans').select('*').eq('loan_id',loan_id).limit(1).execute().data or []
    if not found: raise HTTPException(404,'Loan not found')
    a,i=_choices(); return templates.TemplateResponse(request=request,name='loan_form.html',context={'loan':found[0],'artifacts':a,'institutions':i,'statuses':STATUSES})

@router.post('/loans/{loan_id}/edit')
async def loan_edit(loan_id:str,artifact_id:str=Form(...),institution_id:str=Form(...),loan_date:str=Form(...),expected_return_date:str=Form(...),actual_return_date:str=Form(''),status:str=Form('Pending'),notes:str=Form('')):
    if status not in STATUSES: raise HTTPException(400,'Invalid loan status')
    if status in ['Pending','Active']:
        if artifact_has_open_loan(artifact_id, exclude_loan_id=loan_id): raise HTTPException(409,'This artifact already has another pending or active loan.')
    update_loan(loan_id,{'artifact_id':artifact_id,'institution_id':institution_id,'loan_date':loan_date,'expected_return_date':expected_return_date,'actual_return_date':actual_return_date or None,'status':status,'notes':notes or None})
    return RedirectResponse('/loans',303)

@router.post('/loans/{loan_id}/delete')
async def loan_delete(loan_id:str):
    delete_loan(loan_id); return RedirectResponse('/loans',303)
