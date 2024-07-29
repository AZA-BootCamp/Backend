#pydantic 모델 정의
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str
