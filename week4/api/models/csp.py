"""CSP (Cube Satellite Protocol) header model and bit operations."""

from pydantic import BaseModel, Field

# Bit field sizes.
CSP_ID_PRIO_SIZE = 2
CSP_ID_HOST_SIZE = 5
CSP_ID_PORT_SIZE = 6
CSP_ID_FLAGS_SIZE = 8

# Max values.
CSP_ID_PRIO_MAX = (1 << CSP_ID_PRIO_SIZE) - 1   # 3
CSP_ID_HOST_MAX = (1 << CSP_ID_HOST_SIZE) - 1    # 31
CSP_ID_PORT_MAX = (1 << CSP_ID_PORT_SIZE) - 1    # 63
CSP_ID_FLAGS_MAX = (1 << CSP_ID_FLAGS_SIZE) - 1  # 255

# Bit shifts.
CSP_ID_FLAGS_SHIFT = 0
CSP_ID_SPORT_SHIFT = CSP_ID_FLAGS_SIZE
CSP_ID_DPORT_SHIFT = CSP_ID_SPORT_SHIFT + CSP_ID_PORT_SIZE
CSP_ID_DST_SHIFT = CSP_ID_DPORT_SHIFT + CSP_ID_PORT_SIZE
CSP_ID_SRC_SHIFT = CSP_ID_DST_SHIFT + CSP_ID_HOST_SIZE
CSP_ID_PRIO_SHIFT = CSP_ID_SRC_SHIFT + CSP_ID_HOST_SIZE

# Bit masks.
CSP_ID_PRIO_MASK = CSP_ID_PRIO_MAX << CSP_ID_PRIO_SHIFT
CSP_ID_SRC_MASK = CSP_ID_HOST_MAX << CSP_ID_SRC_SHIFT
CSP_ID_DST_MASK = CSP_ID_HOST_MAX << CSP_ID_DST_SHIFT
CSP_ID_DPORT_MASK = CSP_ID_PORT_MAX << CSP_ID_DPORT_SHIFT
CSP_ID_SPORT_MASK = CSP_ID_PORT_MAX << CSP_ID_SPORT_SHIFT
CSP_ID_FLAGS_MASK = CSP_ID_FLAGS_MAX << CSP_ID_FLAGS_SHIFT

# Flag bits.
CSP_FCRC32 = 0x01
CSP_FRDP = 0x02
CSP_FXTEA = 0x04
CSP_FHMAC = 0x08
CSP_FFRAG = 0x10


class CspHeader(BaseModel):
    """CSP header fields."""

    priority: int = Field(ge=0, le=CSP_ID_PRIO_MAX, description="Priority (0-3)")
    source: int = Field(ge=0, le=CSP_ID_HOST_MAX, description="Source address (0-31)")
    destination: int = Field(
        ge=0, le=CSP_ID_HOST_MAX, description="Destination address (0-31)"
    )
    dport: int = Field(
        ge=0, le=CSP_ID_PORT_MAX, description="Destination port (0-63)"
    )
    sport: int = Field(ge=0, le=CSP_ID_PORT_MAX, description="Source port (0-63)")
    flags: int = Field(ge=0, le=CSP_ID_FLAGS_MAX, description="Flags (0-255)")


def parse(raw: int) -> CspHeader:
    """Parse a 32-bit raw CSP header into structured fields."""
    return CspHeader(
        priority=(raw & CSP_ID_PRIO_MASK) >> CSP_ID_PRIO_SHIFT,
        source=(raw & CSP_ID_SRC_MASK) >> CSP_ID_SRC_SHIFT,
        destination=(raw & CSP_ID_DST_MASK) >> CSP_ID_DST_SHIFT,
        dport=(raw & CSP_ID_DPORT_MASK) >> CSP_ID_DPORT_SHIFT,
        sport=(raw & CSP_ID_SPORT_MASK) >> CSP_ID_SPORT_SHIFT,
        flags=(raw & CSP_ID_FLAGS_MASK) >> CSP_ID_FLAGS_SHIFT,
    )


def serialize(header: CspHeader) -> int:
    """Serialize structured CSP header fields into a 32-bit raw value."""
    return (
        (header.priority << CSP_ID_PRIO_SHIFT)
        | (header.source << CSP_ID_SRC_SHIFT)
        | (header.destination << CSP_ID_DST_SHIFT)
        | (header.dport << CSP_ID_DPORT_SHIFT)
        | (header.sport << CSP_ID_SPORT_SHIFT)
        | (header.flags << CSP_ID_FLAGS_SHIFT)
    )


def from_bytes(buf: bytes) -> CspHeader:
    """Parse 4-byte buffer (big-endian) into structured fields."""
    if len(buf) != 4:
        raise ValueError("CSP header must be exactly 4 bytes")
    raw = int.from_bytes(buf, byteorder="big")
    return parse(raw)


def to_bytes(header: CspHeader) -> bytes:
    """Serialize structured fields into 4-byte buffer (big-endian)."""
    raw = serialize(header)
    return raw.to_bytes(4, byteorder="big")


class CspPacket(BaseModel):
    """CSP packet: header + payload."""

    header: CspHeader
    payload: str = Field(default="", description="Payload as hex string (e.g. '48656C6C6F')")


def parse_packet(data: bytes) -> CspPacket:
    """Parse raw bytes into CSP packet (header + payload)."""
    if len(data) < 4:
        raise ValueError("CSP packet must be at least 4 bytes (header)")
    header = from_bytes(data[:4])
    payload_hex = data[4:].hex().upper()
    return CspPacket(header=header, payload=payload_hex)


def build_packet(packet: CspPacket) -> bytes:
    """Build raw bytes from CSP packet (header + payload)."""
    header_bytes = to_bytes(packet.header)
    payload_bytes = bytes.fromhex(packet.payload) if packet.payload else b""
    return header_bytes + payload_bytes
