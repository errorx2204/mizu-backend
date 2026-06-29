from fastapi import APIRouter, HTTPException
from typing import List
from app.database import supabase

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/")
def create_transaction(transaction: dict, user_id: int):
    result = supabase.table("transactions").insert({
        "user_id": user_id,
        "title": transaction["title"],
        "amount": transaction["amount"],
        "category": transaction["category"],
        "type": transaction["type"]
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create transaction")
    
    return result.data[0]

@router.get("/")
def get_transactions(user_id: int):
    result = supabase.table("transactions")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()
    
    return result.data if result.data else []

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int):
    result = supabase.table("transactions")\
        .delete()\
        .eq("id", transaction_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {"message": "Transaction deleted"}
