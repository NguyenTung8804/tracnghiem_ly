import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def load_filtered_questions(khoi: int, loai: str, nam: int, de_so: int):
    try:
        with open("database.json", "r", encoding="utf-8") as f:
            all_questions = json.load(f)
        return [q for q in all_questions if q.get("khoi_lop") == khoi and q.get("loai_de") == loai and q.get("nam_hoc") == nam and q.get("de_so") == de_so]
    except Exception:
        return []

# 1. TRANG CHỦ MỚI: Hiển thị danh sách 3 đề thi
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )

# 2. TRANG LÀM BÀI: Chuyển sang đường dẫn /thi
@app.get("/thi", response_class=HTMLResponse)
async def read_item(request: Request, de_so: int = 1):
    questions = load_filtered_questions(khoi=12, loai="Thi Dai Hoc", nam=2026, de_so=de_so)
    secure_questions = []
    for q in questions:
        secure_questions.append({
            "id": q["id"], "noi_dung": q["noi_dung"], "cac_lua_chon": q["cac_lua_chon"]
        })
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"questions": secure_questions, "de_so": de_so}
    )

class ExamSubmit(BaseModel):
    answers: Dict[str, str]
    de_so: int

@app.post("/api/submit")
async def submit_exam(data: ExamSubmit):
    questions = load_filtered_questions(khoi=12, loai="Thi Dai Hoc", nam=2026, de_so=data.de_so)
    student_answers = data.answers
    score = 0
    detailed_results = []
    for q in questions:
        q_id_str = str(q["id"])
        chosen = student_answers.get(q_id_str, "Chưa chọn")
        is_correct = (chosen == q["dap_an_dung"])
        if is_correct: score += 1
        detailed_results.append({
            "id": q["id"], "noi_dung": q["noi_dung"], "dap_an_dung": q["dap_an_dung"],
            "chosen": chosen, "is_correct": is_correct, "giai_chi_tiet": q["giai_chi_tiet"]
        })
    return {"score": score, "total": len(questions), "details": detailed_results}

