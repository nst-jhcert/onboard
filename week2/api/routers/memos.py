from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from routers.schemas import MemoCreate, MemoUpdate, MemoResponse
from database import get_db
from models import MemoModel
from cache import get_cache, set_cache, delete_cache

router = APIRouter(tags=["WEEK2"])

@router.get("/", response_model=list[MemoResponse])
def get_memos(db: Session = Depends(get_db)):
    cached = get_cache("memos:all")
    if cached:
        return cached

    memos = db.query(MemoModel).all()
    set_cache("memos:all", [MemoResponse.model_validate(m).model_dump() for m in memos])
    return memos

@router.post("/", status_code=201, response_model=MemoResponse)
def create_memo(memo: MemoCreate, db: Session = Depends(get_db)):
    new_memo = MemoModel(title=memo.title, body=memo.body)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    delete_cache("memos:all")
    return new_memo

@router.get("/{memo_id}", response_model=MemoResponse)
def read_memo(memo_id: int, db: Session = Depends(get_db)):
    cached = get_cache(f"memos:{memo_id}")
    if cached:
        return cached
    
    memo = db.query(MemoModel).filter(MemoModel.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")

    set_cache(f"memos:{memo_id}", MemoResponse.model_validate(memo).model_dump())
    return memo

@router.put("/{memo_id}", response_model=MemoResponse)
def update_memo(memo_id: int, memo: MemoUpdate, db: Session = Depends(get_db)):
    existing = db.query(MemoModel).filter(MemoModel.id == memo_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")

    update_data = memo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)
    delete_cache(f"memos:{memo_id}")
    delete_cache("memos:all")
    return existing

@router.delete("/{memo_id}", status_code=204)
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    memo = db.query(MemoModel).filter(MemoModel.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    db.delete(memo)
    db.commit()
    delete_cache(f"memos:{memo_id}")
    delete_cache("memos:all")
