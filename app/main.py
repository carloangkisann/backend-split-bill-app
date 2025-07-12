from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import SplitRequest
from app.split import calculate_split
from app.pdf_generator import generate_split_pdf
from app.parser import extract_items_from_pdf
import uuid
import shutil
import os
import tempfile
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://split-bill-app-oqoc.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/split/pdf")
def split_and_generate_pdf(data: SplitRequest):
    try:
        results = calculate_split(data)

        pdf_bytes = generate_split_pdf(
            results,
            data.items,
            data.session_id,
            data.total_payment,
            data.handling_fee,
            data.other_fee,
            data.discount,
            data.discount_plus
        )

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=split_summary_{data.session_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/parse")
async def upload_and_parse(file: UploadFile = File(...)):
    temp_file_path = None
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file_path = temp_file.name
        
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        items, total_price, handling_fee, other_fee, discount, discount_plus, total_payment = extract_items_from_pdf(temp_file_path)
        
        os.unlink(temp_file_path)

        return JSONResponse(content={
            "items": items,
            "total_price": total_price,
            "handling_fee": handling_fee,
            "other_fee": other_fee,
            "discount": discount,
            "discount_plus": discount_plus,
            "total_payment": total_payment,
        })

    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))