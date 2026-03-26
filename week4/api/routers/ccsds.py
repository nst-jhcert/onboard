"""CCSDS packet parse/serialize endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models import ccsds as ccsds_model

router = APIRouter()


class ParseRequest(BaseModel):
    """Request body for parsing a raw CCSDS primary header."""

    raw: str = Field(
        description="48-bit CCSDS primary header as hex string (12 hex chars)",
        json_schema_extra={"examples": ["08C6C00A0010"]},
    )


class ParseResponse(BaseModel):
    """Parsed CCSDS primary header fields with raw representations."""

    header: ccsds_model.CcsdsPrimaryHeader
    raw_hex: str
    raw_int: int


class SerializeResponse(BaseModel):
    """Serialized CCSDS primary header raw representations."""

    raw_hex: str
    raw_int: int
    raw_bytes: list[int]


class PacketParseRequest(BaseModel):
    """Request body for parsing a full CCSDS packet."""

    raw: str = Field(
        description="Full CCSDS packet as hex string (header + payload, min 12 hex chars)",
        json_schema_extra={"examples": ["08C6C00A001048656C6C6F"]},
    )


class PacketParseResponse(BaseModel):
    """Parsed CCSDS packet with header fields and payload."""

    header: ccsds_model.CcsdsPrimaryHeader
    payload: str
    raw_hex: str


class PacketBuildRequest(BaseModel):
    """Request body for building a full CCSDS packet."""

    header: ccsds_model.CcsdsPrimaryHeader
    payload: str = Field(default="", description="Payload as hex string")


class PacketBuildResponse(BaseModel):
    """Built CCSDS packet raw representations."""

    raw_hex: str
    raw_bytes: list[int]
    length: int


@router.post("/parse", response_model=ParseResponse)
def parse_ccsds_header(request: ParseRequest):
    """Parse a raw 48-bit value into CCSDS primary header fields."""
    try:
        raw = int(request.raw, 16) if request.raw.startswith(("0x", "0X")) or all(
            c in "0123456789abcdefABCDEF" for c in request.raw
        ) else int(request.raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid raw value")

    if raw < 0 or raw > 0xFFFFFFFFFFFF:
        raise HTTPException(status_code=400, detail="Value must be 0..0xFFFFFFFFFFFF")

    header = ccsds_model.parse(raw)
    return ParseResponse(
        header=header,
        raw_hex=f"{raw:012X}",
        raw_int=raw,
    )


@router.post("/serialize", response_model=SerializeResponse)
def serialize_ccsds_header(header: ccsds_model.CcsdsPrimaryHeader):
    """Serialize CCSDS primary header fields into a raw 48-bit value."""
    raw = ccsds_model.serialize(header)
    raw_bytes = list(raw.to_bytes(ccsds_model.CCSDS_HEADER_SIZE, byteorder="big"))
    return SerializeResponse(
        raw_hex=f"{raw:012X}",
        raw_int=raw,
        raw_bytes=raw_bytes,
    )


@router.post("/packet/parse", response_model=PacketParseResponse)
def parse_ccsds_packet(request: PacketParseRequest):
    """Parse a full CCSDS packet (primary header + payload) from hex string."""
    try:
        data = bytes.fromhex(request.raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hex string")

    if len(data) < ccsds_model.CCSDS_HEADER_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Packet must be at least {ccsds_model.CCSDS_HEADER_SIZE} bytes ({ccsds_model.CCSDS_HEADER_SIZE * 2} hex chars)",
        )

    packet = ccsds_model.parse_packet(data)
    return PacketParseResponse(
        header=packet.header,
        payload=packet.payload,
        raw_hex=data.hex().upper(),
    )


@router.post("/packet/build", response_model=PacketBuildResponse)
def build_ccsds_packet(request: PacketBuildRequest):
    """Build a full CCSDS packet from primary header fields and payload hex."""
    try:
        packet = ccsds_model.CcsdsPacket(header=request.header, payload=request.payload)
        data = ccsds_model.build_packet(packet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PacketBuildResponse(
        raw_hex=data.hex().upper(),
        raw_bytes=list(data),
        length=len(data),
    )
