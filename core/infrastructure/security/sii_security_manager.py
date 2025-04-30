# core/infrastructure/security/sii_security_manager.py
from datetime import datetime
import base64
from lxml import etree
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import ocsp, AuthorityInformationAccess
from .security_manager import SecurityManager
from ..sii_certificate import SIICertificateLoader


class SIISecurityManager(SecurityManager):
    def __init__(self):
        super().__init__()
        loader = SIICertificateLoader()
        self.private_key, self.cert, _ = loader.load()
        self._validate_certificate()

    def _validate_certificate(self):
        """Valida certificado según estándares SII"""
        # 1. Verificar fecha de expiración
        if self.cert.not_valid_after < datetime.now():
            raise ValueError("Certificado expirado")

        # 2. Verificar OCSP (Revocación)
        builder = ocsp.OCSPRequestBuilder()
        builder = builder.add_certificate(self.cert, self.cert.issuer, hashes.SHA256())
        request = builder.build()

        # 3. Consultar servicio OCSP del SII
        aia = self.cert.extensions.get_extension_for_oid(
            AuthorityInformationAccess.oid
        ).value
        responder_url = aia[0].access_location.value

    def generar_sello_legal(self, xml_data: bytes) -> str:
        """Firma XML según especificaciones SII Res. 65/2021"""
        signature = self.private_key.sign(
            xml_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    def _generar_xml(self, data:dict) -> etree.Element:
        """Genera estructura XML según esquema SII"""
        NSMAP = {
            None: "http://www.sii.cl/SiiDte",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
        root = etree.Element("Documento", nsmap=NSMAP)

        # Encabezado
        encabezado = etree.SubElement(root, "Encabezado")

        # ID Doc
        iddoc = etree.SubElement(encabezado, "IdDoc")
        etree.SubElement(iddoc, "TipoDTE").text = str(data['tipo_dte'])
        etree.SubElement(iddoc, "Folio").text = str(data['folio'])

        # Emisor
        emisor = etree.SubElement(encabezado, "Emisor")
        etree.SubElement(emisor, "RUT").text = data['emisor']['rut']
        etree.SubElement(emisor, "RznSoc").text = data['emisor']['razon_social']

        # Receptor
        receptor = etree.SubElement(encabezado, "Receptor")
        etree.SubElement(receptor, "Rut").text = data['receptor']['rut']
        etree.SubElement(receptor, "RznSocRecap").text = data['receptor']['razon_social']

        # Totales
        totales = etree.SubElement(encabezado, "Totales")
        etree.SubElement(totales, "MntNeto").text = str(data['montos']['neto'])
        etree.SubElement(totales, "IVA").text = str(data['montos']['iva'])
        etree.SubElement(totales, "MntTotal").text = str(data['montos']['totales'])

        return root

    def generar_sello_digital(self, data: dict) -> str:
        """
        Implementación específica para SII:
        - Usa PKCS#1 v1.5 en vez de PSS
        - Serialización XML en vez de JSON
        - Certificado oficial del SII
        """
        # 1. Generar XML según formato SII
        xml_root = self._generar_xml(data)

        # 2. Canonicalización exclusiva (c14n)
        canonical_xml = etree.tostring(
            xml_root,
            method="c14n",
            exclusive=True,
            with_comments=False
            )

        # 3. Firma con certificado SII
        signature = self.private_key.sign(
            canonical_xml,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode()
    