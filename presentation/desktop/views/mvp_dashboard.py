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


        self.tree = ttk.Treeview(self, columns=('status'), show='headings')
        self.tree.heading('#0', textr='Componente MVP')
        self.tree.heading('status', text='Estado')

        for item in self.mvp_service.obtener_items():
            status = '✓' if item.completado else '✗'

            self.tree.pack(expand=True, fill=tk.BOTH)

    def _update_status(self):
        self.mvp_service.actualizar_estado()