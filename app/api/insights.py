from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
from app.database import supabase

router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("/{user_id}")
def get_insights(user_id: int):
    """Generate AI-powered spending insights for a user."""
    
    # Fetch all transactions
    transactions_result = supabase.table("transactions")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()
    
    transactions = transactions_result.data if transactions_result.data else []
    
    # Fetch budgets
    budgets_result = supabase.table("budgets")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    
    budgets = budgets_result.data if budgets_result.data else []
    budgets_dict = {b["category"]: b["amount"] for b in budgets}
    
    if not transactions:
        return {
            "insights": [],
            "summary": {
                "total_spent": 0,
                "total_budget": sum(budgets_dict.values()),
                "categories_tracked": len(budgets_dict)
            }
        }
    
    # Calculate current month spending
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1
    
    # Group transactions by month and category
    monthly_spending = defaultdict(lambda: defaultdict(float))
    category_spending = defaultdict(float)
    
    for t in transactions:
        if t["type"] == "expense":
            date = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))
            month_key = f"{date.year}-{date.month:02d}"
            monthly_spending[month_key][t["category"]] += float(t["amount"])
            category_spending[t["category"]] += float(t["amount"])
    
    current_month_key = f"{current_year}-{current_month:02d}"
    last_month_key = f"{last_year}-{last_month:02d}"
    
    insights = []
    
    # 1. Budget vs Actual Analysis
    for category, budget in budgets_dict.items():
        spent = category_spending.get(category, 0)
        remaining = budget - spent
        percent_used = (spent / budget * 100) if budget > 0 else 0
        
        if percent_used > 100:
            insights.append({
                "type": "warning",
                "title": f"Budget Exceeded: {category}",
                "message": f"You've spent ${spent:.2f} on {category}, ${spent - budget:.2f} over your ${budget:.2f} budget.",
                "category": category,
                "severity": "high"
            })
        elif percent_used > 80:
            insights.append({
                "type": "warning",
                "title": f"Budget Almost Full: {category}",
                "message": f"You've used {percent_used:.1f}% of your ${budget:.2f} {category} budget. Only ${remaining:.2f} left.",
                "category": category,
                "severity": "medium"
            })
        elif percent_used < 20 and spent > 0:
            insights.append({
                "type": "positive",
                "title": f"Great Savings: {category}",
                "message": f"You're only at {percent_used:.1f}% of your {category} budget. Keep it up!",
                "category": category,
                "severity": "low"
            })
    
    # 2. Month-over-Month Trends
    if last_month_key in monthly_spending and current_month_key in monthly_spending:
        last_month_total = sum(monthly_spending[last_month_key].values())
        current_month_total = sum(monthly_spending[current_month_key].values())
        
        if last_month_total > 0:
            change_percent = ((current_month_total - last_month_total) / last_month_total) * 100
            
            if change_percent > 20:
                insights.append({
                    "type": "trend",
                    "title": "Spending Increased",
                    "message": f"Your spending is up {change_percent:.1f}% compared to last month (${current_month_total:.2f} vs ${last_month_total:.2f}).",
                    "category": "overall",
                    "severity": "medium"
                })
            elif change_percent < -20:
                insights.append({
                    "type": "positive",
                    "title": "Spending Decreased",
                    "message": f"Great job! Your spending is down {abs(change_percent):.1f}% compared to last month.",
                    "category": "overall",
                    "severity": "low"
                })
    
    # 3. Category Trends (month-over-month per category)
    for category in category_spending.keys():
        if category in monthly_spending.get(current_month_key, {}) and category in monthly_spending.get(last_month_key, {}):
            current = monthly_spending[current_month_key][category]
            last = monthly_spending[last_month_key][category]
            
            if last > 0:
                change = ((current - last) / last) * 100
                if change > 30:
                    insights.append({
                        "type": "trend",
                        "title": f"{category} Spending Surge",
                        "message": f"Your {category} spending jumped {change:.1f}% this month (${current:.2f} vs ${last:.2f} last month).",
                        "category": category,
                        "severity": "medium"
                    })
                elif change < -30:
                    insights.append({
                        "type": "positive",
                        "title": f"{category} Spending Down",
                        "message": f"Nice! Your {category} spending dropped {abs(change):.1f}% this month.",
                        "category": category,
                        "severity": "low"
                    })
    
    # 4. Top Spending Category
    if category_spending:
        top_category = max(category_spending, key=category_spending.get)
        top_amount = category_spending[top_category]
        total_spent = sum(category_spending.values())
        top_percent = (top_amount / total_spent * 100) if total_spent > 0 else 0
        
        if top_percent > 40:
            insights.append({
                "type": "info",
                "title": f"Top Spending: {top_category}",
                "message": f"{top_category} makes up {top_percent:.1f}% of your total spending (${top_amount:.2f} of ${total_spent:.2f}).",
                "category": top_category,
                "severity": "low"
            })
    
    # 5. Smart Suggestions
    total_spent = sum(category_spending.values())
    total_budget = sum(budgets_dict.values())
    
    if total_budget > 0 and total_spent > total_budget:
        over_budget = total_spent - total_budget
        insights.append({
            "type": "suggestion",
            "title": "Over Budget Alert",
            "message": f"You're ${over_budget:.2f} over your total monthly budget. Consider cutting back on non-essential categories.",
            "category": "overall",
            "severity": "high"
        })
    
    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    insights.sort(key=lambda x: severity_order.get(x["severity"], 3))
    
    return {
        "insights": insights,
        "summary": {
            "total_spent": total_spent,
            "total_budget": total_budget,
            "categories_tracked": len(budgets_dict),
            "insights_count": len(insights)
        }
    }
