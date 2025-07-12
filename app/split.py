
from app.models import SplitRequest, PersonSplitResult, ItemAssignment
from typing import List


def calculate_split(data: SplitRequest) -> List[PersonSplitResult]:
    results = []

    for person in data.assignments:
        total = 0
        for item_assignment in person.items:
            item = data.items[item_assignment.item_index]
            if item_assignment.quantity > item.quantity:
                raise ValueError(f"Assigned quantity {item_assignment.quantity} exceeds available quantity {item.quantity} for item '{item.name}'")
            total += item.unit_price * item_assignment.quantity

        results.append(PersonSplitResult(
            name=person.name,
            total=total,
            items=person.items
        ))

    return results
