from typing import Literal, Optional
from pydantic import BaseModel


class DataItem(BaseModel):
    # información general
    num: str
    titular: str
    titulo: str
    fecha: str
    uso_amparado: str
    volumen_total_de_aguas_nacionales: str
    volumen_total_de_aguas_superficiales: str
    volumen_total_de_aguas_subterraneas: str
    volumen_total_de_descargas: str
    anexos_superficiales: int
    anexos_subterraneos: int
    anexos_zonas_federales: int
    anexos_descargas: int
    superficie_total: str
    anotaciones_marginales: str
    tipo_de_anexo: Literal["superficial", "subterraneo", "federal", "descarga"]
    lat: str
    lon: str
    estado: str
    municipio: str
    cuenca: str
    region_hidrologica: str
    acuifero: Optional[str]
    acuifero_homologado: Optional[str]
    volumen: Optional[str]
    corriente_o_vaso: Optional[str]
    superficie: Optional[str]
    fuente: Optional[str]
    afluente: Optional[str]

    # descargas
    cuerpo_receptor: Optional[str]
    descarga_afluente: Optional[str]
    procedencia: Optional[str]
    forma_de_descarga: Optional[str]
    tipo_de_descarga: Optional[str]
    volumen_de_descarga_diario: Optional[str]
    volumen_de_descarga_anual: Optional[str]
