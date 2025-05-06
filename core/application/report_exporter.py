import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


class ReportExporter:
    @staticmethod
    def to_excel(report_data: dict):
        df_lotes = pd.DataFrame(report_data['lotes'])
        df_movimientos = pd.DataFrame(report_data['movimientos'])

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # type: ignore
            df_lotes.to_excel(writer, sheet_name='Lotes', index=False)
            df_movimientos.to_excel(writer, sheet_name='Movimientos', index=False)
        return output.getvalue()

    @staticmethod
    def to_pdf(report_data: dict):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = []

        # Cabecera
        content.append(Paragraph("Reporte de Inventario", styles['Title']))
        content.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        content.append(Spacer(1, 12))

        # Lotes
        content.append(Paragraph("Lotes Registrados:", styles['Heading2']))
        for lote in report_data['lotes']:
            text = f"SKU: {lote['sku']} - Cantidad: {lote['cantidad']} - Costo: ${lote['costo_unitario']:,.2f}"
            content.append(Paragraph(text, styles['Normal']))

        doc.build(content)
        return buffer.getvalue()
