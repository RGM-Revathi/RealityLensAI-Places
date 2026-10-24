from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import re

app = FastAPI(title="FACT CHECK ✓ with RealityLensAI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Illustrative examples only; these are not real customer reviews or live ratings.
PLATFORMS = {
    "Amazon": {"category": "Online Shopping", "url": "https://www.amazon.in/", "description": "Product listings, seller experience, delivery, returns and refunds.", "reviews": [
        {"perspective": "Family shopper", "text": "The order arrived on time and tracking updates were helpful.", "rating": 4},
        {"perspective": "Student", "text": "The refund process took longer than expected.", "rating": 2},
        {"perspective": "First-time buyer", "text": "The product page clearly listed the main features.", "rating": 4},
        {"perspective": "Working professional", "text": "Resolving a support issue took several steps.", "rating": 3},
    ]},
    "Flipkart": {"category": "Online Shopping", "url": "https://www.flipkart.com/", "description": "Listing accuracy, delivery, replacement, returns and support.", "reviews": [
        {"perspective": "Student", "text": "Price comparison was easy and the parcel arrived in good condition.", "rating": 4},
        {"perspective": "Family shopper", "text": "The replacement status was unclear.", "rating": 2},
        {"perspective": "First-time buyer", "text": "The product description could explain accessories more clearly.", "rating": 3},
        {"perspective": "Professional", "text": "Order tracking was useful throughout delivery.", "rating": 4},
    ]},
    "Swiggy": {"category": "Food Delivery", "url": "https://www.swiggy.com/", "description": "Delivery estimates, order accuracy, food condition, fees and support.", "reviews": [
        {"perspective": "Family customer", "text": "The order arrived late and the food was not warm.", "rating": 2},
        {"perspective": "Student", "text": "Tracking was useful and the order was packed neatly.", "rating": 4},
        {"perspective": "Busy professional", "text": "Getting help for a missing item took too long.", "rating": 2},
        {"perspective": "Regular customer", "text": "Reordering a previous meal was quick and convenient.", "rating": 4},
    ]},
    "Zomato": {"category": "Food Delivery", "url": "https://www.zomato.com/", "description": "Restaurant listings, delivery, packaging, fees, refunds and issue resolution.", "reviews": [
        {"perspective": "Family customer", "text": "Restaurant options were easy to compare.", "rating": 4},
        {"perspective": "Student", "text": "The delivery was delayed and arrival time kept changing.", "rating": 2},
        {"perspective": "Professional", "text": "The meal was correct, but resolving a spilled item was unclear.", "rating": 3},
        {"perspective": "Regular customer", "text": "The menu photos helped me choose what to order.", "rating": 4},
    ]},
    "Blinkit": {"category": "Quick Commerce", "url": "https://blinkit.com/", "description": "Stock accuracy, substitutions, missing products, delivery and refunds.", "reviews": [
        {"perspective": "Family shopper", "text": "An unavailable item was substituted without clear communication.", "rating": 2},
        {"perspective": "Student", "text": "Finding daily essentials and checking prices was convenient.", "rating": 4},
        {"perspective": "Professional", "text": "The missing-item refund was not explained clearly.", "rating": 2},
        {"perspective": "Regular customer", "text": "The order arrived quickly and items were packed neatly.", "rating": 4},
    ]},
    "Zepto": {"category": "Quick Commerce", "url": "https://www.zeptonow.com/", "description": "Delivery speed, stock accuracy, item condition, fees and support.", "reviews": [
        {"perspective": "Student", "text": "Repeat ordering was convenient and delivery was quick.", "rating": 4},
        {"perspective": "Family shopper", "text": "Some items were unavailable after checkout and alternatives were unclear.", "rating": 2},
        {"perspective": "Professional", "text": "An item was damaged and the support steps were unclear.", "rating": 2},
        {"perspective": "Regular customer", "text": "The app made it easy to find common grocery items.", "rating": 4},
    ]},
    "BigBasket": {"category": "Grocery Delivery", "url": "https://www.bigbasket.com/", "description": "Grocery freshness, missing items, delivery slots, substitutions and refunds.", "reviews": [
        {"perspective": "Family shopper", "text": "The delivery slot was convenient and groceries arrived in good condition.", "rating": 4},
        {"perspective": "Senior customer", "text": "Some fresh items were not in the expected condition.", "rating": 2},
        {"perspective": "Professional", "text": "Refund status for an unavailable item needed clearer updates.", "rating": 2},
        {"perspective": "Regular customer", "text": "The scheduled slot made weekly grocery shopping easier.", "rating": 4},
    ]},
}

POSITIVE = {"good", "great", "excellent", "clean", "friendly", "helpful", "delicious", "fresh", "comfortable", "fast", "quick", "affordable", "easy", "perfect", "convenient", "on-time", "useful", "neatly"}
NEGATIVE = {"bad", "poor", "dirty", "rude", "slow", "late", "delayed", "delay", "expensive", "stale", "broken", "wrong", "missing", "damaged", "leaking", "terrible", "worst", "unclear", "unavailable", "spilled"}
ASPECTS = {
    "Delivery time": ["delivery", "late", "delayed", "delay", "quick", "fast", "tracking", "slot", "on time"],
    "Order accuracy / availability": ["missing", "wrong", "unavailable", "substituted", "replacement", "order"],
    "Product / food condition": ["food", "warm", "fresh", "stale", "damaged", "spilled", "condition", "packaging", "packed"],
    "Price / fees / value": ["price", "cost", "expensive", "cheap", "fee", "refund", "value"],
    "App / customer support": ["support", "help", "unclear", "communication", "description", "tracking", "updates"],
}

class AnalyzeRequest(BaseModel):
    platform: str = Field(min_length=1, max_length=100)
    review: str = Field(min_length=3, max_length=5000)
    perspective: str = Field(default="General customer", max_length=100)

class ClaimRequest(BaseModel):
    claim: str = Field(min_length=3, max_length=3000)
    evidence: str = Field(default="", max_length=5000)

@app.get("/")
def root():
    return {"name": "FACT CHECK ✓ with RealityLensAI", "status": "running", "docs": "/docs", "note": "Demo backend; review examples are illustrative."}

@app.get("/api/platforms")
def get_platforms():
    return [{"name": name, "category": data["category"], "url": data["url"], "description": data["description"], "review_count": len(data["reviews"])} for name, data in PLATFORMS.items()]

@app.get("/api/platforms/{name}")
def get_platform(name: str):
    if name not in PLATFORMS:
        return {"error": "Platform not found"}
    item = PLATFORMS[name]
    analysis = analyze_reviews(item["reviews"])
    return {"name": name, "category": item["category"], "url": item["url"], "description": item["description"], "reviews": item["reviews"], **analysis}

def analyze_text(text: str):
    words = re.findall(r"[a-z]+(?:-[a-z]+)?", text.lower())
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Mixed / Neutral"
    lower = text.lower()
    aspects = [{"name": name, "matched_terms": [term for term in terms if term in lower]} for name, terms in ASPECTS.items() if any(term in lower for term in terms)]
    # These sentence snippets are candidate claims only; no external evidence is checked.
    claims = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) >= 8]
    return {"sentiment": sentiment, "positive_word_count": pos, "negative_word_count": neg, "aspects": aspects, "candidate_claims": [{"text": c, "evidence_status": "Insufficient evidence", "note": "Review text alone does not verify this statement."} for c in claims]}

def analyze_reviews(reviews):
    rows = []
    for r in reviews:
        result = analyze_text(r["text"])
        rows.append({**r, **result, "evidence_status": "Not independently verified"})
    avg = round(sum(r["rating"] for r in reviews) / max(1, len(reviews)), 1)
    return {"average_rating": avg, "positive_count": sum(r["sentiment"] == "Positive" for r in rows), "negative_count": sum(r["sentiment"] == "Negative" for r in rows), "mixed_count": sum(r["sentiment"] == "Mixed / Neutral" for r in rows), "reviews": rows, "limitations": ["Illustrative sample data only; not live customer reviews.", "Sentiment is keyword-based, not a trained ML prediction.", "Claims and evidence are not independently verified."]}

@app.post("/api/analyze")
def analyze_custom_review(request: AnalyzeRequest):
    result = analyze_text(request.review)
    return {"platform": request.platform, "perspective": request.perspective, "review": request.review, **result, "evidence_status": "Not independently verified", "limitations": ["Keyword-based demo analysis, not a trained ML model.", "No external evidence verification is performed."]}

@app.post("/api/check-claim")
def check_claim(request: ClaimRequest):
    return {"claim": request.claim, "evidence_provided": bool(request.evidence.strip()), "status": "UNVERIFIED", "reason": "This prototype does not authenticate evidence or compare independent sources.", "next_steps": ["Check the original source and date.", "Confirm evidence authenticity and context.", "Compare with independent sources.", "Use human review for disputed claims."], "evidence_note": request.evidence.strip() or "No evidence details supplied."}

@app.get("/api/compare")
def compare_platforms():
    result = []
    for name, data in PLATFORMS.items():
        analysis = analyze_reviews(data["reviews"])
        score = max(0, min(100, round(50 + (analysis["average_rating"] - 3) * 10 - analysis["negative_count"] * 2)))
        result.append({"name": name, "category": data["category"], "average_rating": analysis["average_rating"], "demo_score": score, "review_count": len(data["reviews"]), "note": "Illustrative catalogue score, not an official ranking."})
    return sorted(result, key=lambda x: x["demo_score"], reverse=True)
