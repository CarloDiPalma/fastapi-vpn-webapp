from sqlalchemy.ext.asyncio import AsyncSession

from app.payment.models import Payment


def parse_notification_data(json: dict) -> dict:
    """Parse json data from Yookassa from payment notification endpoint."""
    obj = json.get("object")
    description = obj.get("description")
    status = obj.get("status")
    amount = obj.get("amount").get("value")
    payment_uuid = obj.get("id")
    metadata = obj.get("metadata")
    tariff_id = metadata.get("tariff_id")
    user_id = metadata.get("user_id")
    return {
        "description": description,
        "status": status,
        "amount": amount,
        "payment_uuid": payment_uuid,
        "tariff_id": tariff_id,
        "user_id": user_id
    }


async def create_db_payment(json_body: dict, db: AsyncSession) -> None:
    """Create Payment object in db."""
    if not json_body:
        print('No JSON')
    payment_dict = parse_notification_data(json_body)

    db_payment = Payment(
        **payment_dict,
        payment_url="None", outstanding_balance=1000
    )
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
