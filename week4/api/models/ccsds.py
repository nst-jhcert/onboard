"""CCSDS Space Packet Primary Header model and bit operations."""

from pydantic import BaseModel, Field

# Bit field sizes.
CCSDS_VERSION_SIZE = 3
CCSDS_TYPE_SIZE = 1
CCSDS_SEC_HDR_FLAG_SIZE = 1
CCSDS_APID_SIZE = 11
CCSDS_SEQ_FLAGS_SIZE = 2
CCSDS_SEQ_COUNT_SIZE = 14
CCSDS_DATA_LENGTH_SIZE = 16

# Max values.
CCSDS_VERSION_MAX = (1 << CCSDS_VERSION_SIZE) - 1        # 7
CCSDS_TYPE_MAX = (1 << CCSDS_TYPE_SIZE) - 1              # 1
CCSDS_SEC_HDR_FLAG_MAX = (1 << CCSDS_SEC_HDR_FLAG_SIZE) - 1  # 1
CCSDS_APID_MAX = (1 << CCSDS_APID_SIZE) - 1             # 2047
CCSDS_SEQ_FLAGS_MAX = (1 << CCSDS_SEQ_FLAGS_SIZE) - 1   # 3
CCSDS_SEQ_COUNT_MAX = (1 << CCSDS_SEQ_COUNT_SIZE) - 1   # 16383
CCSDS_DATA_LENGTH_MAX = (1 << CCSDS_DATA_LENGTH_SIZE) - 1  # 65535

# Bit shifts (48-bit, MSB-first).
# [Version(3)][Type(1)][SecHdrFlag(1)][APID(11)][SeqFlags(2)][SeqCount(14)][DataLength(16)]
CCSDS_DATA_LENGTH_SHIFT = 0
CCSDS_SEQ_COUNT_SHIFT = CCSDS_DATA_LENGTH_SIZE
CCSDS_SEQ_FLAGS_SHIFT = CCSDS_SEQ_COUNT_SHIFT + CCSDS_SEQ_COUNT_SIZE
CCSDS_APID_SHIFT = CCSDS_SEQ_FLAGS_SHIFT + CCSDS_SEQ_FLAGS_SIZE
CCSDS_SEC_HDR_FLAG_SHIFT = CCSDS_APID_SHIFT + CCSDS_APID_SIZE
CCSDS_TYPE_SHIFT = CCSDS_SEC_HDR_FLAG_SHIFT + CCSDS_SEC_HDR_FLAG_SIZE
CCSDS_VERSION_SHIFT = CCSDS_TYPE_SHIFT + CCSDS_TYPE_SIZE

# Bit masks.
CCSDS_VERSION_MASK = CCSDS_VERSION_MAX << CCSDS_VERSION_SHIFT
CCSDS_TYPE_MASK = CCSDS_TYPE_MAX << CCSDS_TYPE_SHIFT
CCSDS_SEC_HDR_FLAG_MASK = CCSDS_SEC_HDR_FLAG_MAX << CCSDS_SEC_HDR_FLAG_SHIFT
CCSDS_APID_MASK = CCSDS_APID_MAX << CCSDS_APID_SHIFT
CCSDS_SEQ_FLAGS_MASK = CCSDS_SEQ_FLAGS_MAX << CCSDS_SEQ_FLAGS_SHIFT
CCSDS_SEQ_COUNT_MASK = CCSDS_SEQ_COUNT_MAX << CCSDS_SEQ_COUNT_SHIFT
CCSDS_DATA_LENGTH_MASK = CCSDS_DATA_LENGTH_MAX << CCSDS_DATA_LENGTH_SHIFT

# Header size in bytes.
CCSDS_HEADER_SIZE = 6


class CcsdsPrimaryHeader(BaseModel):
    """CCSDS Space Packet Primary Header fields."""

    version: int = Field(ge=0, le=CCSDS_VERSION_MAX, description="Version (0-7)")
    type: int = Field(ge=0, le=CCSDS_TYPE_MAX, description="Type (0=TM, 1=TC)")
    sec_hdr_flag: int = Field(
        ge=0, le=CCSDS_SEC_HDR_FLAG_MAX, description="Secondary Header Flag (0-1)"
    )
    apid: int = Field(ge=0, le=CCSDS_APID_MAX, description="APID (0-2047)")
    seq_flags: int = Field(
        ge=0, le=CCSDS_SEQ_FLAGS_MAX, description="Sequence Flags (0-3)"
    )
    seq_count: int = Field(
        ge=0, le=CCSDS_SEQ_COUNT_MAX, description="Sequence Count (0-16383)"
    )
    data_length: int = Field(
        ge=0, le=CCSDS_DATA_LENGTH_MAX, description="Data Length (0-65535)"
    )


def parse(raw: int) -> CcsdsPrimaryHeader:
    """Parse a 48-bit raw CCSDS primary header into structured fields."""
    return CcsdsPrimaryHeader(
        version=(raw & CCSDS_VERSION_MASK) >> CCSDS_VERSION_SHIFT,
        type=(raw & CCSDS_TYPE_MASK) >> CCSDS_TYPE_SHIFT,
        sec_hdr_flag=(raw & CCSDS_SEC_HDR_FLAG_MASK) >> CCSDS_SEC_HDR_FLAG_SHIFT,
        apid=(raw & CCSDS_APID_MASK) >> CCSDS_APID_SHIFT,
        seq_flags=(raw & CCSDS_SEQ_FLAGS_MASK) >> CCSDS_SEQ_FLAGS_SHIFT,
        seq_count=(raw & CCSDS_SEQ_COUNT_MASK) >> CCSDS_SEQ_COUNT_SHIFT,
        data_length=((raw & CCSDS_DATA_LENGTH_MASK) >> CCSDS_DATA_LENGTH_SHIFT) + 1,
    )


def serialize(header: CcsdsPrimaryHeader) -> int:
    """Serialize structured CCSDS primary header fields into a 48-bit raw value."""
    return (
        (header.version << CCSDS_VERSION_SHIFT)
        | (header.type << CCSDS_TYPE_SHIFT)
        | (header.sec_hdr_flag << CCSDS_SEC_HDR_FLAG_SHIFT)
        | (header.apid << CCSDS_APID_SHIFT)
        | (header.seq_flags << CCSDS_SEQ_FLAGS_SHIFT)
        | (header.seq_count << CCSDS_SEQ_COUNT_SHIFT)
        | ((header.data_length - 1) << CCSDS_DATA_LENGTH_SHIFT)
    )


def from_bytes(buf: bytes) -> CcsdsPrimaryHeader:
    """Parse 6-byte buffer (big-endian) into structured fields."""
    if len(buf) != CCSDS_HEADER_SIZE:
        raise ValueError(f"CCSDS primary header must be exactly {CCSDS_HEADER_SIZE} bytes")
    raw = int.from_bytes(buf, byteorder="big")
    return parse(raw)


def to_bytes(header: CcsdsPrimaryHeader) -> bytes:
    """Serialize structured fields into 6-byte buffer (big-endian)."""
    raw = serialize(header)
    return raw.to_bytes(CCSDS_HEADER_SIZE, byteorder="big")


class CcsdsPacket(BaseModel):
    """CCSDS packet: primary header + payload."""

    header: CcsdsPrimaryHeader
    payload: str = Field(default="", description="Payload as hex string")


def parse_packet(data: bytes) -> CcsdsPacket:
    """Parse raw bytes into CCSDS packet (primary header + payload)."""
    if len(data) < CCSDS_HEADER_SIZE:
        raise ValueError(f"CCSDS packet must be at least {CCSDS_HEADER_SIZE} bytes (primary header)")
    header = from_bytes(data[:CCSDS_HEADER_SIZE])
    payload_hex = data[CCSDS_HEADER_SIZE:].hex().upper()
    return CcsdsPacket(header=header, payload=payload_hex)


def build_packet(packet: CcsdsPacket) -> bytes:
    """Build raw bytes from CCSDS packet (primary header + payload)."""
    header_bytes = to_bytes(packet.header)
    payload_bytes = bytes.fromhex(packet.payload) if packet.payload else b""
    return header_bytes + payload_bytes
