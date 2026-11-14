from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import supabase
from app.services.collection_service import all_collections, collection_by_id, collection_artifacts, add_artifacts, remove_artifact

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

def rows(table, order):
    return supabase.table(table).select("*").order(order, desc=(order == "created_at")).execute().data or []

@router.get("/artists", response_class=HTMLResponse)
async def artists_page(request: Request):
    artists = rows("artists", "name")
    return templates.TemplateResponse(request=request, name="collection/artists.html", context={"artists":artists})

@router.get("/artists/add", response_class=HTMLResponse)
async def artist_add_page(request: Request):
    return templates.TemplateResponse(request=request, name="collection/artist_form.html", context={"artist":{}})

@router.post("/artists/add")
async def artist_add(name:str=Form(...), birth_year:str=Form(""), death_year:str=Form(""), nationality:str=Form(""), biography:str=Form("")):
    supabase.table("artists").insert({"name":name.strip(),"birth_year":int(birth_year) if birth_year else None,"death_year":int(death_year) if death_year else None,"nationality":nationality or None,"biography":biography or None}).execute()
    return RedirectResponse("/artists",303)

@router.get("/artists/{artist_id}/edit", response_class=HTMLResponse)
async def artist_edit_page(request:Request, artist_id:str):
    r=supabase.table("artists").select("*").eq("artist_id",artist_id).execute().data or []
    if not r:return HTMLResponse("Artist not found",404)
    return templates.TemplateResponse(request=request,name="collection/artist_form.html",context={"artist":r[0]})

@router.post("/artists/{artist_id}/edit")
async def artist_edit(artist_id:str,name:str=Form(...),birth_year:str=Form(""),death_year:str=Form(""),nationality:str=Form(""),biography:str=Form("")):
    supabase.table("artists").update({"name":name.strip(),"birth_year":int(birth_year) if birth_year else None,"death_year":int(death_year) if death_year else None,"nationality":nationality or None,"biography":biography or None}).eq("artist_id",artist_id).execute()
    return RedirectResponse("/artists",303)

@router.post("/artists/{artist_id}/delete")
async def artist_delete(artist_id:str):
    supabase.table("artists").delete().eq("artist_id",artist_id).execute()
    return RedirectResponse("/artists",303)

@router.get("/categories", response_class=HTMLResponse)
async def categories_page(request:Request):
    return templates.TemplateResponse(request=request,name="collection/categories.html",context={"categories":rows("categories","category_name")})

@router.get("/categories/add", response_class=HTMLResponse)
async def category_add_page(request:Request):
    return templates.TemplateResponse(request=request,name="collection/category_form.html",context={"category":{}})

@router.post("/categories/add")
async def category_add(category_name:str=Form(...),description:str=Form("")):
    supabase.table("categories").insert({"category_name":category_name.strip(),"description":description or None}).execute()
    return RedirectResponse("/categories",303)

@router.get("/categories/{category_id}/edit",response_class=HTMLResponse)
async def category_edit_page(request:Request,category_id:str):
    r=supabase.table("categories").select("*").eq("category_id",category_id).execute().data or []
    if not r:return HTMLResponse("Category not found",404)
    return templates.TemplateResponse(request=request,name="collection/category_form.html",context={"category":r[0]})

@router.post("/categories/{category_id}/edit")
async def category_edit(category_id:str,category_name:str=Form(...),description:str=Form("")):
    supabase.table("categories").update({"category_name":category_name.strip(),"description":description or None}).eq("category_id",category_id).execute()
    return RedirectResponse("/categories",303)

@router.post("/categories/{category_id}/delete")
async def category_delete(category_id:str):
    supabase.table("categories").delete().eq("category_id",category_id).execute()
    return RedirectResponse("/categories",303)

@router.get("/acquisitions",response_class=HTMLResponse)
async def acquisitions_page(request:Request):
    data=supabase.table("acquisitions").select("*, artifacts(title)").order("acquisition_date",desc=True).execute().data or []
    artifacts=rows("artifacts","title")
    return templates.TemplateResponse(request=request,name="collection/acquisitions.html",context={"acquisitions":data,"artifacts":artifacts})

@router.get("/acquisitions/add",response_class=HTMLResponse)
async def acquisition_add_page(request:Request):
    return templates.TemplateResponse(request=request,name="collection/acquisition_form.html",context={"artifacts":rows("artifacts","title")})

@router.post("/acquisitions/add")
async def acquisition_add(artifact_id:str=Form(...),acquisition_type:str=Form(...),acquisition_date:str=Form(...),source_name:str=Form(""),purchase_price:str=Form(""),notes:str=Form("")):
    supabase.table("acquisitions").insert({"artifact_id":artifact_id,"acquisition_type":acquisition_type,"acquisition_date":acquisition_date,"source_name":source_name or None,"purchase_price":float(purchase_price) if purchase_price else None,"notes":notes or None}).execute()
    return RedirectResponse("/acquisitions",303)

@router.post("/acquisitions/{acquisition_id}/delete")
async def acquisition_delete(acquisition_id:str):
    supabase.table("acquisitions").delete().eq("acquisition_id",acquisition_id).execute()
    return RedirectResponse("/acquisitions",303)

@router.get("/collections",response_class=HTMLResponse)
async def collections_page(request:Request):
    return templates.TemplateResponse(request=request,name="collections/collections.html",context={"collections":all_collections()})

@router.get("/collections/add",response_class=HTMLResponse)
async def collection_add_page(request:Request):
    return templates.TemplateResponse(request=request,name="collections/collection_form.html",context={"collection":{}})

@router.post("/collections/add")
async def collection_add(name:str=Form(...),description:str=Form("")):
    supabase.table("collections").insert({"name":name.strip(),"description":description or None}).execute()
    return RedirectResponse("/collections",303)

@router.get("/collections/{collection_id}",response_class=HTMLResponse)
async def collection_detail_page(request:Request,collection_id:int):
    c=collection_by_id(collection_id)
    if not c:return HTMLResponse("Collection not found",404)
    return templates.TemplateResponse(request=request,name="collections/collection_details.html",context={"collection":c,"artifacts":collection_artifacts(collection_id)})

@router.get("/collections/{collection_id}/edit",response_class=HTMLResponse)
async def collection_edit_page(request:Request,collection_id:int):
    c=collection_by_id(collection_id)
    if not c:return HTMLResponse("Collection not found",404)
    return templates.TemplateResponse(request=request,name="collections/collection_form.html",context={"collection":c})

@router.post("/collections/{collection_id}/edit")
async def collection_edit(collection_id:int,name:str=Form(...),description:str=Form("")):
    supabase.table("collections").update({"name":name.strip(),"description":description or None}).eq("collection_id",collection_id).execute()
    return RedirectResponse(f"/collections/{collection_id}",303)

@router.post("/collections/{collection_id}/delete")
async def collection_delete(collection_id:int):
    supabase.table("collection_artifacts").delete().eq("collection_id",collection_id).execute()
    supabase.table("collections").delete().eq("collection_id",collection_id).execute()
    return RedirectResponse("/collections",303)

@router.post("/collections/{collection_id}/star")
async def collection_star(collection_id:int):
    c=collection_by_id(collection_id)
    if c:supabase.table("collections").update({"is_starred":not c["is_starred"]}).eq("collection_id",collection_id).execute()
    return RedirectResponse("/collections",303)

@router.post("/collections/{collection_id}/feature")
async def collection_feature(collection_id:int):
    c=collection_by_id(collection_id)
    if c:supabase.table("collections").update({"is_featured":not c["is_featured"]}).eq("collection_id",collection_id).execute()
    return RedirectResponse("/collections",303)

@router.get("/collections/{collection_id}/add-artifacts",response_class=HTMLResponse)
async def collection_add_artifacts_page(request:Request,collection_id:int):
    c=collection_by_id(collection_id)
    if not c:return HTMLResponse("Collection not found",404)
    artifacts=rows("artifacts","title")
    linked={a["artifact_id"] for a in collection_artifacts(collection_id)}
    available=[a for a in artifacts if a["artifact_id"] not in linked]
    return templates.TemplateResponse(request=request,name="collections/add_artifacts.html",context={"collection":c,"artifacts":available})

@router.post("/collections/{collection_id}/add-artifacts")
async def collection_add_artifacts(collection_id:int,artifact_ids:list[str]=Form([])):
    add_artifacts(collection_id,artifact_ids)
    return RedirectResponse(f"/collections/{collection_id}",303)

@router.post("/collections/{collection_id}/remove/{artifact_id}")
async def collection_remove_artifact(collection_id:int,artifact_id:str):
    remove_artifact(collection_id,artifact_id)
    return RedirectResponse(f"/collections/{collection_id}",303)
