import json
from datetime import datetime
from typing import List, Optional
from models import Producto, Venta

class Database:
    def __init__(self):
        self.productos_file = "productos.json"
        self.ventas_file = "ventas.json"
        self.load_data()

    def load_data(self):
        try:
            with open(self.productos_file, 'r') as f:
                productos_data = json.load(f)
                self.productos = [Producto(**p) for p in productos_data]
        except FileNotFoundError:
            self.productos = []

        try:
            with open(self.ventas_file, 'r') as f:
                ventas_data = json.load(f)
                self.ventas = [
                    Venta(
                        id=v["id"],
                        fecha=datetime.fromisoformat(v["fecha"]),
                        productos=v["productos"],
                        total=v["total"]
                    ) for v in ventas_data
                ]
        except FileNotFoundError:
            self.ventas = []

    def save_data(self):
        with open(self.productos_file, 'w') as f:
            json.dump([p.to_dict() for p in self.productos], f)
        
        with open(self.ventas_file, 'w') as f:
            json.dump([v.to_dict() for v in self.ventas], f)

    def agregar_producto(self, producto: Producto):
        self.productos.append(producto)
        self.save_data()

    def actualizar_producto(self, producto: Producto):
        for i, p in enumerate(self.productos):
            if p.id == producto.id:
                self.productos[i] = producto
                break
        self.save_data()

    def eliminar_producto(self, producto_id: int):
        self.productos = [p for p in self.productos if p.id != producto_id]
        self.save_data()

    def buscar_producto(self, nombre: str) -> List[Producto]:
        return [p for p in self.productos if nombre.lower() in p.nombre.lower()]

    def obtener_producto_por_id(self, producto_id: int) -> Optional[Producto]:
        for producto in self.productos:
            if producto.id == producto_id:
                return producto
        return None

    def registrar_venta(self, venta: Venta):
        self.ventas.append(venta)
        for producto_vendido in venta.productos:
            producto = self.obtener_producto_por_id(producto_vendido["id"])
            if producto:
                producto.cantidad -= producto_vendido["cantidad"]
                self.actualizar_producto(producto)
        self.save_data()