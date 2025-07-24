from pydantic import BaseModel, ConfigDict
from datetime import datetime

class FotoPromotorBase(BaseModel):
    url_foto: str
    legenda: str | None = None
    loja: str | None = None
    cidade: str | None = None

class FotoPromotor(FotoPromotorBase):
    id: int
    promotor_id: int
    empresa_id: int
    data_envio: datetime

    model_config = ConfigDict(from_attributes=True)