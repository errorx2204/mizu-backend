from fastapi import APIRouter, HTTPException
from typing import List
from app.database import supabase

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/")
def create_budget(budget: dict, user_id: int):
    result = supabase.table("budgets").insert({
        "user_id": user_id,
        "category": budget["category"],
        "amount": budget["amount"]
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create budget")
    
    return result.data[0]

@router.get("/")
def get_budgets(user_id: int):
    result = supabase.table("budgets")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    
    return result.data if result.data else []

@router.put("/{budget_id}")
def update_budget(budget_id: int, budget: dict):
    result = supabase.table("budgets")\
        .update({
            "category": budget["category"],
            "amount": budget["amount"]
        })\
        .eq("id", budget_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return result.data[0]

@router.delete("/{budget_id}")
def delete_budget(budget_id: int):
    result = supabase.table("budgets")\
        .delete()\
        .eq("id", budget_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {"message": "Budget deleted"}
