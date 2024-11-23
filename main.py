import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from db import Database
from models import Producto, Venta

class InventoryApp:
    def __init__(self):
        self.db = Database()
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Productos"

    def run(self):
        st.title("Sistema de Gestión de Inventario")
        
        menu = ["Productos", "Ventas", "Informes"]
        st.session_state.current_page = st.sidebar.selectbox("Menú", menu)

        if st.session_state.current_page == "Productos":
            self.mostrar_productos()
        elif st.session_state.current_page == "Ventas":
            self.mostrar_ventas()
        else:
            self.mostrar_informes()

    def mostrar_productos(self):
        st.header("Gestión de Productos")
        
        # Formulario para agregar/editar productos
        with st.form("producto_form"):
            producto_id = st.number_input("ID del Producto", min_value=1, step=1)
            nombre = st.text_input("Nombre del Producto")
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            cantidad = st.number_input("Cantidad", min_value=0, step=1)
            categoria = st.text_input("Categoría")
            stock_minimo = st.number_input("Stock Mínimo", min_value=1, step=1, value=5)
            
            submitted = st.form_submit_button("Guardar Producto")
            
            if submitted and nombre and precio > 0:
                nuevo_producto = Producto(
                    id=producto_id,
                    nombre=nombre,
                    precio=precio,
                    cantidad=cantidad,
                    categoria=categoria,
                    stock_minimo=stock_minimo
                )
                self.db.agregar_producto(nuevo_producto)
                st.success("Producto guardado exitosamente")

        # Mostrar productos
        if self.db.productos:
            df = pd.DataFrame([p.to_dict() for p in self.db.productos])
            st.dataframe(df)

            # Alertas de stock bajo
            productos_stock_bajo = [p for p in self.db.productos if p.cantidad <= p.stock_minimo]
            if productos_stock_bajo:
                st.warning("¡Productos con stock bajo!")
                for p in productos_stock_bajo:
                    st.write(f"- {p.nombre}: {p.cantidad} unidades (Mínimo: {p.stock_minimo})")

    def mostrar_ventas(self):
        st.header("Registro de Ventas")
        
        # Selección de productos para la venta
        productos_venta = []
        productos_disponibles = [p for p in self.db.productos if p.cantidad > 0]
        
        if not productos_disponibles:
            st.warning("No hay productos disponibles para la venta")
            return

        with st.form("venta_form"):
            producto_seleccionado = st.selectbox(
                "Seleccionar Producto",
                options=productos_disponibles,
                format_func=lambda x: f"{x.nombre} (Stock: {x.cantidad})"
            )
            
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=producto_seleccionado.cantidad if producto_seleccionado else 0,
                step=1
            )
            
            if st.form_submit_button("Agregar a la Venta"):
                productos_venta.append({
                    "id": producto_seleccionado.id,
                    "nombre": producto_seleccionado.nombre,
                    "cantidad": cantidad,
                    "precio_unitario": producto_seleccionado.precio,
                    "subtotal": producto_seleccionado.precio * cantidad
                })
                st.session_state.productos_venta = productos_venta

        if 'productos_venta' in st.session_state and st.session_state.productos_venta:
            st.write("### Productos en la venta actual:")
            df_venta = pd.DataFrame(st.session_state.productos_venta)
            st.dataframe(df_venta)
            
            total_venta = sum(item["subtotal"] for item in st.session_state.productos_venta)
            st.write(f"Total de la venta: ${total_venta:.2f}")
            
            if st.button("Finalizar Venta"):
                venta = Venta(
                    id=len(self.db.ventas) + 1,
                    fecha=datetime.now(),
                    productos=st.session_state.productos_venta,
                    total=total_venta
                )
                self.db.registrar_venta(venta)
                st.session_state.productos_venta = []
                st.success("Venta registrada exitosamente")

    def mostrar_informes(self):
        st.header("Informes de Ventas")
        
        # Selector de período
        periodo = st.selectbox(
            "Seleccionar período",
            ["Diario", "Semanal", "Mensual"]
        )
        
        # Filtrar ventas según el período seleccionado
        fecha_actual = datetime.now()
        if periodo == "Diario":
            fecha_inicio = fecha_actual.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == "Semanal":
            fecha_inicio = fecha_actual - timedelta(days=7)
        else:  # Mensual
            fecha_inicio = fecha_actual - timedelta(days=30)
            
        ventas_filtradas = [
            v for v in self.db.ventas
            if v.fecha >= fecha_inicio
        ]
        
        if ventas_filtradas:
            # Resumen de ventas
            total_ventas = sum(v.total for v in ventas_filtradas)
            cantidad_ventas = len(ventas_filtradas)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Ventas", f"${total_ventas:.2f}")
            with col2:
                st.metric("Cantidad de Ventas", cantidad_ventas)
            
            # Detalle de ventas
            df_ventas = pd.DataFrame([
                {
                    "Fecha": v.fecha,
                    "ID": v.id,
                    "Total": v.total,
                    "Productos": len(v.productos)
                }
                for v in ventas_filtradas
            ])
            st.write("### Detalle de Ventas")
            st.dataframe(df_ventas)
            
            # Productos más vendidos
            productos_vendidos = {}
            for venta in ventas_filtradas:
                for producto in venta.productos:
                    if producto["id"] in productos_vendidos:
                        productos_vendidos[producto["id"]]["cantidad"] += producto["cantidad"]
                        productos_vendidos[producto["id"]]["total"] += producto["subtotal"]
                    else:
                        productos_vendidos[producto["id"]] = {
                            "nombre": producto["nombre"],
                            "cantidad": producto["cantidad"],
                            "total": producto["subtotal"]
                        }
            
            df_productos = pd.DataFrame(productos_vendidos.values())
            if not df_productos.empty:
                st.write("### Productos Más Vendidos")
                st.dataframe(df_productos.sort_values(by="cantidad", ascending=False))
        else:
            st.info(f"No hay ventas registradas para el período {periodo.lower()}")

if __name__ == "__main__":
    app = InventoryApp()
    app.run()