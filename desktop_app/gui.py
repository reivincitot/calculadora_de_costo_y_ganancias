import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://localhost:8000"

# Funciones API
def agregar_lote():
    sku = sku_entry_lote.get()
    cantidad = cantidad_entry_lote.get()
    costo = costo_entry_lote.get()

    if not sku or not cantidad or not costo:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        data = {
            "sku": sku,
            "cantidad": int(cantidad),
            "costo": float(costo)
        }
        response = requests.post(f"{API_URL}/inventory/batches", json=data)
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Lote agregado exitosamente.")
        else:
            messagebox.showerror("Error", f"Error al agregar lote: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {str(e)}")


def consultar_stock():
    sku = sku_entry_consulta.get()
    if not sku:
        messagebox.showerror("Error", "El campo SKU es obligatorio.")
        return
    try:
        response = requests.get(f"{API_URL}/inventory/stock/{sku}")
        if response.status_code == 200:
            stock_data = response.json()
            stock_actual = stock_data.get("stock_actual")
            messagebox.showinfo("Stock Actual", f"El stock actual de {sku} es: {stock_actual}")
        else:
            messagebox.showerror("Error", f"No se encontró el SKU: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {str(e)}")


def consumir_stock():
    sku = sku_entry_consumo.get()
    cantidad = cantidad_entry_consumo.get()

    if not sku or not cantidad:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        response = requests.post(f"{API_URL}/inventory/consume/{sku}", json={"quantity": int(cantidad)})
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Stock consumido exitosamente.")
        else:
            messagebox.showerror("Error", response.text)
    except Exception as e:
        messagebox.showerror("Error", str(e))


# === UI ===
root = tk.Tk()
root.title("Gestión de Inventario")
root.geometry("400x300")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Pestaña 1: Agregar Lote
frame_lote = ttk.Frame(notebook)
notebook.add(frame_lote, text="Agregar Lote")

tk.Label(frame_lote, text="SKU:").pack()
sku_entry_lote = tk.Entry(frame_lote)
sku_entry_lote.pack()

tk.Label(frame_lote, text="Cantidad:").pack()
cantidad_entry_lote = tk.Entry(frame_lote)
cantidad_entry_lote.pack()

tk.Label(frame_lote, text="Costo unitario:").pack()
costo_entry_lote = tk.Entry(frame_lote)
costo_entry_lote.pack()

tk.Button(frame_lote, text="Agregar", command=agregar_lote).pack(pady=10)

# Pestaña 2: Consultar Stock
frame_consulta = ttk.Frame(notebook)
notebook.add(frame_consulta, text="Consultar Stock")

tk.Label(frame_consulta, text="SKU:").pack()
sku_entry_consulta = tk.Entry(frame_consulta)
sku_entry_consulta.pack()

tk.Button(frame_consulta, text="Consultar", command=consultar_stock).pack(pady=10)

# Pestaña 3: Consumir Stock
frame_consumo = ttk.Frame(notebook)
notebook.add(frame_consumo, text="Consumir Stock")

tk.Label(frame_consumo, text="SKU:").pack()
sku_entry_consumo = tk.Entry(frame_consumo)
sku_entry_consumo.pack()

tk.Label(frame_consumo, text="Cantidad:").pack()
cantidad_entry_consumo = tk.Entry(frame_consumo)
cantidad_entry_consumo.pack()

tk.Button(frame_consumo, text="Consumir", command=consumir_stock).pack(pady=10)

# Iniciar la app
root.mainloop()
