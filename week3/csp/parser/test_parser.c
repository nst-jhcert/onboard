#include "csp_parser.h"

#include <stdio.h>
#include <string.h>

static int g_tests_passed = 0;
static int g_tests_failed = 0;

#define ASSERT_EQ(a, b)                                                  \
  do {                                                                   \
    if ((a) != (b)) {                                                    \
      printf("  => FAIL (line %d: 0x%X != 0x%X)\n\n", __LINE__,         \
             (unsigned)(a), (unsigned)(b));                               \
      g_tests_failed++;                                                  \
      return;                                                            \
    }                                                                    \
  } while (0)

#define RUN_TEST(fn)                              \
  do {                                            \
    printf("--- %-34s ---\n", #fn);               \
    fn();                                         \
  } while (0)

#define PASS()                                    \
  do {                                            \
    printf("  => PASS\n\n");                      \
    g_tests_passed++;                             \
  } while (0)

// Formats a raw 32-bit header into a single-line string with hex and fields.
static void FormatRaw(char *buf, size_t len, uint32_t raw) {
  snprintf(buf, len,
           "0x%08X [PRI=%u SRC=%2u DST=%2u DP=%2u SP=%2u FL=0x%02X]",
           raw,
           (raw >> 30) & 0x3,
           (raw >> 25) & 0x1F,
           (raw >> 20) & 0x1F,
           (raw >> 14) & 0x3F,
           (raw >> 8) & 0x3F,
           raw & 0xFF);
}

// Logs TX(sent) vs RX(received) comparison.
static void LogLoopback(uint32_t raw_in, uint32_t raw_out) {
  char tx[128], rx[128];
  FormatRaw(tx, sizeof(tx), raw_in);
  FormatRaw(rx, sizeof(rx), raw_out);
  printf("  TX: %s\n", tx);
  printf("  RX: %s\n", rx);
}

// Logs byte-level TX/RX comparison.
static void LogLoopbackBytes(const uint8_t in[4], const uint8_t out[4]) {
  printf("  TX: [%02X %02X %02X %02X]\n", in[0], in[1], in[2], in[3]);
  printf("  RX: [%02X %02X %02X %02X]\n", out[0], out[1], out[2], out[3]);
}

// Builds a raw 32-bit CSP header from individual field values using direct bit
// shifts — independent of the parser implementation.
static uint32_t BuildRawHeader(uint8_t pri, uint8_t src, uint8_t dst,
                               uint8_t dport, uint8_t sport, uint8_t flags) {
  return ((uint32_t)pri << 30) |
         ((uint32_t)src << 25) |
         ((uint32_t)dst << 20) |
         ((uint32_t)dport << 14) |
         ((uint32_t)sport << 8) |
         ((uint32_t)flags);
}

// Loopback: build raw bits -> parse -> serialize -> compare raw.
static void TestLoopbackBasic(void) {
  uint32_t raw_in = BuildRawHeader(2, 10, 5, 1, 20, CSP_FRDP | CSP_FCRC32);

  CspHeader header;
  ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);

  uint32_t raw_out;
  ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

  LogLoopback(raw_in, raw_out);
  ASSERT_EQ(raw_out, raw_in);
  PASS();
}

// Loopback: all-zero.
static void TestLoopbackZero(void) {
  uint32_t raw_in = BuildRawHeader(0, 0, 0, 0, 0, 0x00);

  CspHeader header;
  ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);

  uint32_t raw_out;
  ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

  LogLoopback(raw_in, raw_out);
  ASSERT_EQ(raw_out, raw_in);
  ASSERT_EQ(raw_out, 0u);
  PASS();
}

// Loopback: all-max (0xFFFFFFFF).
static void TestLoopbackMax(void) {
  uint32_t raw_in = BuildRawHeader(3, 31, 31, 63, 63, 0xFF);
  ASSERT_EQ(raw_in, 0xFFFFFFFFu);

  CspHeader header;
  ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);

  uint32_t raw_out;
  ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

  LogLoopback(raw_in, raw_out);
  ASSERT_EQ(raw_out, raw_in);
  PASS();
}

// Loopback: each priority level.
static void TestLoopbackPriorities(void) {
  for (uint8_t pri = 0; pri <= 3; pri++) {
    uint32_t raw_in = BuildRawHeader(pri, 1, 2, 3, 4, 0x00);

    CspHeader header;
    ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);
    ASSERT_EQ(header.priority, pri);

    uint32_t raw_out;
    ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

    printf("  [pri=%u] TX=0x%08X  RX=0x%08X\n", pri, raw_in, raw_out);
    ASSERT_EQ(raw_out, raw_in);
  }
  PASS();
}

// Loopback: each individual flag bit.
static void TestLoopbackFlagBits(void) {
  const char *flag_names[] = {
    "CRC32", "RDP", "XTEA", "HMAC", "FRAG", "RES3", "RES2", "RES1",
  };
  uint8_t flag_bits[] = {
    CSP_FCRC32, CSP_FRDP, CSP_FXTEA, CSP_FHMAC,
    CSP_FFRAG, CSP_FRES3, CSP_FRES2, CSP_FRES1,
  };

  for (size_t i = 0; i < sizeof(flag_bits) / sizeof(flag_bits[0]); i++) {
    uint32_t raw_in = BuildRawHeader(0, 0, 0, 0, 0, flag_bits[i]);

    CspHeader header;
    ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);
    ASSERT_EQ(header.flags, flag_bits[i]);

    uint32_t raw_out;
    ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

    printf("  [%-5s 0x%02X] TX=0x%08X  RX=0x%08X\n",
           flag_names[i], flag_bits[i], raw_in, raw_out);
    ASSERT_EQ(raw_out, raw_in);
  }
  PASS();
}

// Loopback: combined flag combinations.
static void TestLoopbackFlagCombos(void) {
  uint8_t combos[] = {
    CSP_FRDP | CSP_FCRC32,
    CSP_FHMAC | CSP_FXTEA | CSP_FRDP,
    CSP_FFRAG | CSP_FHMAC | CSP_FXTEA | CSP_FRDP | CSP_FCRC32,
    0xFF,
  };

  for (size_t i = 0; i < sizeof(combos) / sizeof(combos[0]); i++) {
    uint32_t raw_in = BuildRawHeader(1, 15, 16, 32, 33, combos[i]);

    CspHeader header;
    ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);

    uint32_t raw_out;
    ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

    printf("  [flags=0x%02X] TX=0x%08X  RX=0x%08X\n",
           combos[i], raw_in, raw_out);
    ASSERT_EQ(raw_out, raw_in);
  }
  PASS();
}

// Loopback: sweep all source addresses.
static void TestLoopbackSrcSweep(void) {
  for (uint8_t src = 0; src <= CSP_ID_HOST_MAX; src++) {
    uint32_t raw_in = BuildRawHeader(0, src, 0, 0, 0, 0);

    CspHeader header;
    ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);
    ASSERT_EQ(header.source, src);

    uint32_t raw_out;
    ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);
    ASSERT_EQ(raw_out, raw_in);
  }
  printf("  src=[0..%d] all %d values matched\n",
         CSP_ID_HOST_MAX, CSP_ID_HOST_MAX + 1);
  PASS();
}

// Loopback: sweep all destination ports.
static void TestLoopbackDportSweep(void) {
  for (uint8_t dp = 0; dp <= CSP_ID_PORT_MAX; dp++) {
    uint32_t raw_in = BuildRawHeader(0, 0, 0, dp, 0, 0);

    CspHeader header;
    ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);
    ASSERT_EQ(header.dport, dp);

    uint32_t raw_out;
    ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);
    ASSERT_EQ(raw_out, raw_in);
  }
  printf("  dport=[0..%d] all %d values matched\n",
         CSP_ID_PORT_MAX, CSP_ID_PORT_MAX + 1);
  PASS();
}

// Loopback via bytes: raw -> bytes -> parse -> serialize -> bytes -> compare.
static void TestLoopbackBytes(void) {
  uint32_t raw_in = BuildRawHeader(1, 31, 0, 63, 0, 0xFF);

  uint8_t buf_in[4] = {
    (raw_in >> 24) & 0xFF,
    (raw_in >> 16) & 0xFF,
    (raw_in >> 8) & 0xFF,
    raw_in & 0xFF,
  };

  CspHeader header;
  ASSERT_EQ(CspHeaderFromBytes(buf_in, &header), 0);

  uint8_t buf_out[4];
  ASSERT_EQ(CspHeaderToBytes(&header, buf_out), 0);

  LogLoopbackBytes(buf_in, buf_out);
  ASSERT_EQ(buf_out[0], buf_in[0]);
  ASSERT_EQ(buf_out[1], buf_in[1]);
  ASSERT_EQ(buf_out[2], buf_in[2]);
  ASSERT_EQ(buf_out[3], buf_in[3]);
  PASS();
}

// Loopback: broadcast packet (dst=31, dport=0 CMP service).
static void TestLoopbackBroadcast(void) {
  uint32_t raw_in = BuildRawHeader(kCspPrioCritical, 1, 31, 0, 10, CSP_FHMAC);

  CspHeader header;
  ASSERT_EQ(CspHeaderParse(raw_in, &header), 0);

  uint32_t raw_out;
  ASSERT_EQ(CspHeaderSerialize(&header, &raw_out), 0);

  LogLoopback(raw_in, raw_out);
  ASSERT_EQ(raw_out, raw_in);
  PASS();
}

// Validate that serialize rejects out-of-range fields.
static void TestSerializeRejectsOutOfRange(void) {
  uint32_t raw;

  CspHeader bad_pri = {.priority = 4};
  ASSERT_EQ(CspHeaderSerialize(&bad_pri, &raw), -1);

  CspHeader bad_src = {.source = 32};
  ASSERT_EQ(CspHeaderSerialize(&bad_src, &raw), -1);

  CspHeader bad_dst = {.destination = 32};
  ASSERT_EQ(CspHeaderSerialize(&bad_dst, &raw), -1);

  CspHeader bad_dp = {.dport = 64};
  ASSERT_EQ(CspHeaderSerialize(&bad_dp, &raw), -1);

  CspHeader bad_sp = {.sport = 64};
  ASSERT_EQ(CspHeaderSerialize(&bad_sp, &raw), -1);

  printf("  all 5 out-of-range cases rejected\n");
  PASS();
}

// Validate NULL pointer safety.
static void TestNullSafety(void) {
  uint32_t raw;
  CspHeader header = {0};

  ASSERT_EQ(CspHeaderParse(0, NULL), -1);
  ASSERT_EQ(CspHeaderSerialize(NULL, &raw), -1);
  ASSERT_EQ(CspHeaderSerialize(&header, NULL), -1);
  ASSERT_EQ(CspHeaderFromBytes(NULL, &header), -1);
  ASSERT_EQ(CspHeaderToBytes(&header, NULL), -1);

  printf("  all 5 NULL cases rejected\n");
  PASS();
}

int main(void) {
  printf("=== CSP Parser Loopback Tests ===\n\n");

  RUN_TEST(TestLoopbackBasic);
  RUN_TEST(TestLoopbackZero);
  RUN_TEST(TestLoopbackMax);
  RUN_TEST(TestLoopbackPriorities);
  RUN_TEST(TestLoopbackFlagBits);
  RUN_TEST(TestLoopbackFlagCombos);
  RUN_TEST(TestLoopbackSrcSweep);
  RUN_TEST(TestLoopbackDportSweep);
  RUN_TEST(TestLoopbackBytes);
  RUN_TEST(TestLoopbackBroadcast);
  RUN_TEST(TestSerializeRejectsOutOfRange);
  RUN_TEST(TestNullSafety);

  printf("=================================\n");
  printf("Results: %d passed, %d failed\n", g_tests_passed, g_tests_failed);
  return g_tests_failed ? 1 : 0;
}
