from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import json

@dataclass
class Producto:
    id: int
    nombre: str
    precio: float
    cantidad: int
    categoria: str
    stock_minimo: int = 5

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "cantidad": self.cantidad,
            "categoria": self.categoria,
            "stock_minimo": self.stock_minimo
        }

@dataclass
class Venta:
    id: int
    fecha: datetime
    productos: List[Dict]
    total: float

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "productos": self.productos,
            "total": self.total
        }
