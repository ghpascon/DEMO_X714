from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.future import select
from io import StringIO
import csv
from app.schemas.logger import log_error, log_info
from app.db.database import get_db
from app.models.rfid import DbTag
from app.schemas.X714 import reader
from fastapi.responses import RedirectResponse
from typing import Optional
router = APIRouter(prefix="/reader")

@router.get("/start")
async def start():
    await reader.start_inventory()
    return 200

@router.get("/stop")
async def stop():
    await reader.stop_inventory()
    return 200

@router.get("/clear")
async def stop():
    await reader.clear_tags()
    return 200

@router.get("/get_tags")
async def get_tags():
    tags_info = []
    current_tags = dict(reader.tags)  # Cópia do dicionário atual

    total = {
        "epc": "Total",
        "tid": "",
        "ant": "",
        "rssi": len(current_tags)
    }
    tags_info.append(total)

    for tag in current_tags:
        tag_data = current_tags.get(tag)
        if tag_data is None:
            continue
        current_tag = {
            "epc": tag_data.get("epc"),
            "tid": tag_data.get("tid"),
            "ant": tag_data.get("ant"),
            "rssi": tag_data.get("rssi")
        }
        tags_info.append(current_tag)

    return tags_info

@router.get("/reader_state")
async def reader_state():
    if not reader.is_connected:
        state = '❌ Leitor desconectado'
    elif reader.is_reading:
        state = '🔍 Realizando leitura das Tags'
    else:
        state = '🛑 Aguardando leitura...'
    return {"state":state}

@router.get("/set_gpo")
async def set_gpo(request: Request):
    gpo = request.query_params.get("gpo")
    state = request.query_params.get("state")
    
    await reader.set_gpo(int(gpo), state)
    
    return {"message": "GPO command received", "gpo": gpo, "state": state}

@router.post("/write_epc")
async def write_epc(
    target_identifier: str = Form(...),
    target_value: Optional[str] = Form(None),
    new_epc: str = Form(...),
    password: str = Form(...)
):
    if target_identifier == "None":
        target_value = None  

    alerts = await reader.write_epc(
        {
            "target_identifier": target_identifier,
            "target_value": target_value,
            "new_epc": new_epc,
            "password": password,
        }
    )
    print(alerts)
    if alerts:
        return RedirectResponse(f"/?msg={alerts[0]} &classe=alert-danger", 303)
    return RedirectResponse("/", 303)

@router.get("/get_report")
async def get_report(request: Request):
    try:
        async with get_db() as db: 
            result = await db.execute(select(DbTag))
            rows = result.fetchall()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([column.name for column in DbTag.__table__.columns])

        for row in rows:
            writer.writerow([getattr(row[0], column.name) for column in DbTag.__table__.columns])

        output.seek(0)
        log_info("Relatório gerado")
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=report.csv"}
        )

    except Exception as e:
        log_error(f"Falha ao gerar relatório: {e}")
        return Response(content=f"Failed to get report: {str(e)}", status_code=500)
    
@router.post("/config")
async def write_epc(
    power: int = Form(...),
    session: int = Form(...),
):
    await reader.config_reader(power=power, session=session)
    return RedirectResponse(f"/?msg=Reader config success &classe=alert-success", 303)
