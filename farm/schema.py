from ninja import Schema

class GoatSchema(Schema):
    id: int
    name: str
    breed: str
    age: int
    buy_price: float