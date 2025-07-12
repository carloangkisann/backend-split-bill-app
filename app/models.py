from pydantic import BaseModel, Field
from typing import List


class Item(BaseModel):
    name: str
    quantity: int = Field(..., ge=1)
    unit_price: int = Field(..., ge=0)

class ItemAssignment(BaseModel):
    item_index: int = Field(..., ge=0)
    quantity: int = Field(..., ge=1)

class PersonAssignment(BaseModel):
    name: str
    items: List[ItemAssignment]

class SplitRequest(BaseModel):
    session_id: str
    items: List[Item]
    assignments: List[PersonAssignment]
    total_payment: int
    discount: int
    discount_plus: int
    handling_fee: int
    other_fee: int

class PersonSplitResult(BaseModel):
    name: str
    total: int  
    items: List[ItemAssignment]  
