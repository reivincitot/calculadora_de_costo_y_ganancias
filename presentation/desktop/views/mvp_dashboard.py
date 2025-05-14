import tkinter as tk
from tkinter import ttk
from core.application.mvp_service import MVPStatusService


class MVPDashboard(tk.Toplevel):
    def __init__(self, parent, mvp_service: MVPStatusService):
        super().__init__(parent)
        self.mvp_service = mvp_service
        self._build_ui()
        self._update_status()

    def _build_ui(self):
        self.title("Seguimiento MVP - ISO 9001")
        self.geometry("600x400")

        self.tree = ttk.Treeview(self, columns=('componente', 'estado'), show='headings')
        self.tree.heading('componente', text='Componente MVP')
        self.tree.heading('estado', text='Estado')
        self.tree.pack(expand=True, fill=tk.BOTH)



    def _update_status(self):
        for item in self.mvp_service.obtener_items():
            estado = '✓' if item.completado else '✗'
            self.tree.insert('', 'end', values=(item.nombre, estado))
