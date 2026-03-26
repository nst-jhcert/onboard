"""CSP packet parse/serialize endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models import csp as csp_model

router = APIRouter()


class ParseRequest(BaseModel):
    """Request body for parsing a raw CSP header."""

    raw: str = Field(
        description="32-bit CSP header as hex string (e.g. 'A5143403') or decimal integer string",
        json_schema_extra={"examples": ["A5143403"]},
    )


class ParseResponse(BaseModel):
    """Parsed CSP header fields with raw representations."""

    header: csp_model.CspHeader
    raw_hex: str
    raw_int: int


class SerializeResponse(BaseModel):
    """Serialized CSP header raw representations."""

    raw_hex: str
    raw_int: int
    raw_bytes: list[int]


@router.post("/parse", response_model=ParseResponse)
def parse_csp_header(request: ParseRequest):
    """Parse a raw 32-bit value into CSP header fields."""
    try:
        raw = int(request.raw, 16) if request.raw.startswith(("0x", "0X")) or all(
            c in "0123456789abcdefABCDEF" for c in request.raw
        ) else int(request.raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid raw value")

    if raw < 0 or raw > 0xFFFFFFFF:
        raise HTTPException(status_code=400, detail="Value must be 0..0xFFFFFFFF")

    header = csp_model.parse(raw)
    return ParseResponse(
        header=header,
        raw_hex=f"{raw:08X}",
        raw_int=raw,
    )


@router.post("/serialize", response_model=SerializeResponse)
def serialize_csp_header(header: csp_model.CspHeader):
    """Serialize CSP header fields into a raw 32-bit value."""
    raw = csp_model.serialize(header)
    raw_bytes = list(raw.to_bytes(4, byteorder="big"))
    return SerializeResponse(
        raw_hex=f"{raw:08X}",
        raw_int=raw,
        raw_bytes=raw_bytes,
    )


class PacketParseRequest(BaseModel):
    """Request body for parsing a full CSP packet."""

    raw: str = Field(
        description="Full CSP packet as hex string (header + payload, min 8 hex chars)",
        json_schema_extra={"examples": ["A514340348656C6C6F"]},
    )


class PacketParseResponse(BaseModel):
    """Parsed CSP packet with header fields and payload."""

    header: csp_model.CspHeader
    payload: str
    raw_hex: str


class PacketBuildRequest(BaseModel):
    """Request body for building a full CSP packet."""

    header: csp_model.CspHeader
    payload: str = Field(
        default="",
        description="Payload as hex string (e.g. '48656C6C6F')",
    )


class PacketBuildResponse(BaseModel):
    """Built CSP packet raw representations."""

    raw_hex: str
    raw_bytes: list[int]
    length: int


@router.post("/packet/parse", response_model=PacketParseResponse)
def parse_csp_packet(request: PacketParseRequest):
    """Parse a full CSP packet (header + payload) from hex string."""
    try:
        data = bytes.fromhex(request.raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hex string")

    if len(data) < 4:
        raise HTTPException(
            status_code=400,
            detail="Packet must be at least 4 bytes (8 hex chars)",
        )

    packet = csp_model.parse_packet(data)
    return PacketParseResponse(
        header=packet.header,
        payload=packet.payload,
        raw_hex=data.hex().upper(),
    )


@router.post("/packet/build", response_model=PacketBuildResponse)
def build_csp_packet(request: PacketBuildRequest):
    """Build a full CSP packet from header fields and payload hex."""
    try:
        packet = csp_model.CspPacket(header=request.header, payload=request.payload)
        data = csp_model.build_packet(packet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PacketBuildResponse(
        raw_hex=data.hex().upper(),
        raw_bytes=list(data),
        length=len(data),
    )
