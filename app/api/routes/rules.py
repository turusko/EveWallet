from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.rule import RuleCreate, RuleOut, RuleRunRequest, RuleRunResponse, RuleUpdate
from app.services.assignment_rule_service import AssignmentRuleService

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("", response_model=RuleOut)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AssignmentRuleService(db).create(str(user.id), payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[RuleOut])
def list_rules(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return AssignmentRuleService(db).list(str(user.id))


@router.get("/{rule_id}", response_model=RuleOut)
def get_rule(rule_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = AssignmentRuleService(db).get(str(user.id), rule_id)
    if not row:
        raise HTTPException(status_code=404, detail="Rule not found")
    return row


@router.patch("/{rule_id}", response_model=RuleOut)
def update_rule(rule_id: str, payload: RuleUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AssignmentRuleService(db).update(str(user.id), rule_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        AssignmentRuleService(db).delete(str(user.id), rule_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"deleted": True}


@router.post("/run", response_model=RuleRunResponse)
def run_rules(payload: RuleRunRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    count = AssignmentRuleService(db).run(str(user.id), payload)
    return RuleRunResponse(assignments_created=count)
