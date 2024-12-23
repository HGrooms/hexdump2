#!/usr/bin/env python3
import array
import contextlib
import importlib
import os
import sys
import tempfile
import unittest
from io import StringIO
from os import environ, linesep
from types import GeneratorType
from unittest.mock import patch

import hexdump2.__main__

from hexdump2 import hd, hexdump

single_line_result = (
    f"00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
    f"00000010"
)
double_line_result = (
    f"00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
    f"*{linesep}"
    f"00000020"
)

nine_range_result = (
    "00000000  00 01 02 03 04 05 06 07  08                       |.........|\n00000009"
)

nine_range_color_result = r"""[32m00000000  [39m00 [36m01 [36m02 [36m03 [36m04 [36m05 [36m06 [36m07  [36m08                       [39m|[39m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m00000009[39m"""

if os.name == "nt":
    nine_range_color_result = f"{linesep}".join(
        nine_range_color_result.splitlines(False)
    )

nine_bytes_result = (
    "00000000  00 00 00 00 00 00 00 00  00                       |.........|\n00000009"
)

range_0x100_result = r"""00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  |................|
00000010  10 11 12 13 14 15 16 17  18 19 1a 1b 1c 1d 1e 1f  |................|
00000020  20 21 22 23 24 25 26 27  28 29 2a 2b 2c 2d 2e 2f  | !"#$%&'()*+,-./|
00000030  30 31 32 33 34 35 36 37  38 39 3a 3b 3c 3d 3e 3f  |0123456789:;<=>?|
00000040  40 41 42 43 44 45 46 47  48 49 4a 4b 4c 4d 4e 4f  |@ABCDEFGHIJKLMNO|
00000050  50 51 52 53 54 55 56 57  58 59 5a 5b 5c 5d 5e 5f  |PQRSTUVWXYZ[\]^_|
00000060  60 61 62 63 64 65 66 67  68 69 6a 6b 6c 6d 6e 6f  |`abcdefghijklmno|
00000070  70 71 72 73 74 75 76 77  78 79 7a 7b 7c 7d 7e 7f  |pqrstuvwxyz{|}~.|
00000080  80 81 82 83 84 85 86 87  88 89 8a 8b 8c 8d 8e 8f  |................|
00000090  90 91 92 93 94 95 96 97  98 99 9a 9b 9c 9d 9e 9f  |................|
000000a0  a0 a1 a2 a3 a4 a5 a6 a7  a8 a9 aa ab ac ad ae af  |................|
000000b0  b0 b1 b2 b3 b4 b5 b6 b7  b8 b9 ba bb bc bd be bf  |................|
000000c0  c0 c1 c2 c3 c4 c5 c6 c7  c8 c9 ca cb cc cd ce cf  |................|
000000d0  d0 d1 d2 d3 d4 d5 d6 d7  d8 d9 da db dc dd de df  |................|
000000e0  e0 e1 e2 e3 e4 e5 e6 e7  e8 e9 ea eb ec ed ee ef  |................|
000000f0  f0 f1 f2 f3 f4 f5 f6 f7  f8 f9 fa fb fc fd fe ff  |................|
00000100"""

if os.name == "nt":
    range_0x100_result = f"{os.linesep}".join(range_0x100_result.splitlines(False))

colored_ascii_range = r"""[32m00000000  [39m00 [36m01 [36m02 [36m03 [36m04 [36m05 [36m06 [36m07  [36m08 [36m09 [36m0a [36m0b [36m0c [36m0d [36m0e [36m0f  [39m|[39m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m00000010  [36m10 [36m11 [36m12 [36m13 [36m14 [36m15 [36m16 [36m17  [36m18 [36m19 [36m1a [36m1b [36m1c [36m1d [36m1e [36m1f  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m00000020  [33m20 [33m21 [33m22 [33m23 [33m24 [33m25 [33m26 [33m27  [33m28 [33m29 [33m2a [33m2b [33m2c [33m2d [33m2e [33m2f  [39m|[33m [33m![33m"[33m#[33m$[33m%[33m&[33m'[33m([33m)[33m*[33m+[33m,[33m-[33m.[33m/[39m|
[32m00000030  [33m30 [33m31 [33m32 [33m33 [33m34 [33m35 [33m36 [33m37  [33m38 [33m39 [33m3a [33m3b [33m3c [33m3d [33m3e [33m3f  [39m|[33m0[33m1[33m2[33m3[33m4[33m5[33m6[33m7[33m8[33m9[33m:[33m;[33m<[33m=[33m>[33m?[39m|
[32m00000040  [33m40 [33m41 [33m42 [33m43 [33m44 [33m45 [33m46 [33m47  [33m48 [33m49 [33m4a [33m4b [33m4c [33m4d [33m4e [33m4f  [39m|[33m@[33mA[33mB[33mC[33mD[33mE[33mF[33mG[33mH[33mI[33mJ[33mK[33mL[33mM[33mN[33mO[39m|
[32m00000050  [33m50 [33m51 [33m52 [33m53 [33m54 [33m55 [33m56 [33m57  [33m58 [33m59 [33m5a [33m5b [33m5c [33m5d [33m5e [33m5f  [39m|[33mP[33mQ[33mR[33mS[33mT[33mU[33mV[33mW[33mX[33mY[33mZ[33m[[33m\[33m][33m^[33m_[39m|
[32m00000060  [33m60 [33m61 [33m62 [33m63 [33m64 [33m65 [33m66 [33m67  [33m68 [33m69 [33m6a [33m6b [33m6c [33m6d [33m6e [33m6f  [39m|[33m`[33ma[33mb[33mc[33md[33me[33mf[33mg[33mh[33mi[33mj[33mk[33ml[33mm[33mn[33mo[39m|
[32m00000070  [33m70 [33m71 [33m72 [33m73 [33m74 [33m75 [33m76 [33m77  [33m78 [33m79 [33m7a [33m7b [33m7c [33m7d [33m7e [36m7f  [39m|[33mp[33mq[33mr[33ms[33mt[33mu[33mv[33mw[33mx[33my[33mz[33m{[33m|[33m}[33m~[36m.[39m|
[32m00000080  [36m80 [36m81 [36m82 [36m83 [36m84 [36m85 [36m86 [36m87  [36m88 [36m89 [36m8a [36m8b [36m8c [36m8d [36m8e [36m8f  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m00000090  [36m90 [36m91 [36m92 [36m93 [36m94 [36m95 [36m96 [36m97  [36m98 [36m99 [36m9a [36m9b [36m9c [36m9d [36m9e [36m9f  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m000000a0  [36ma0 [36ma1 [36ma2 [36ma3 [36ma4 [36ma5 [36ma6 [36ma7  [36ma8 [36ma9 [36maa [36mab [36mac [36mad [36mae [36maf  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m000000b0  [36mb0 [36mb1 [36mb2 [36mb3 [36mb4 [36mb5 [36mb6 [36mb7  [36mb8 [36mb9 [36mba [36mbb [36mbc [36mbd [36mbe [36mbf  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m000000c0  [36mc0 [36mc1 [36mc2 [36mc3 [36mc4 [36mc5 [36mc6 [36mc7  [36mc8 [36mc9 [36mca [36mcb [36mcc [36mcd [36mce [36mcf  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m000000d0  [36md0 [36md1 [36md2 [36md3 [36md4 [36md5 [36md6 [36md7  [36md8 [36md9 [36mda [36mdb [36mdc [36mdd [36mde [36mdf  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m000000e0  [36me0 [36me1 [36me2 [36me3 [36me4 [36me5 [36me6 [36me7  [36me8 [36me9 [36mea [36meb [36mec [36med [36mee [36mef  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m000000f0  [36mf0 [36mf1 [36mf2 [36mf3 [36mf4 [36mf5 [36mf6 [36mf7  [36mf8 [36mf9 [36mfa [36mfb [36mfc [36mfd [36mfe [36mff  [39m|[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[36m.[39m|
[32m00000100[39m"""

if os.name == "nt":
    colored_ascii_range = f"{linesep}".join(colored_ascii_range.splitlines(False))

colored_0x100_nulls = r"""[32m00000000  [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00  [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00  [39m|[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m|
[31m*
[32m00000100[39m"""

if os.name == "nt":
    colored_0x100_nulls = f"{linesep}".join(colored_0x100_nulls.splitlines(False))


class TestHexdump2(unittest.TestCase):
    def test_bad_return(self):
        with self.assertRaises(ValueError):
            hexdump(bytes(16), "bad_arg")  # noqa

    def test_return_print(self):
        data = bytes(16)
        with StringIO() as buf, contextlib.redirect_stdout(buf):
            hexdump(data)
            buf.seek(0)
            r = buf.read()
            self.assertEqual(single_line_result + linesep, r)

    def test_return_print_newline_at_end(self):
        data = bytes(16)
        with StringIO() as buf, contextlib.redirect_stdout(buf):
            hexdump(data)
            print("Hello", end=linesep)

            buf.seek(0)
            r = buf.read()
            self.assertEqual(single_line_result + linesep + f"Hello{linesep}", r)

    def test_return_generator(self):
        data = bytes(16)
        r = hexdump(data, result="generator")

        self.assertTrue(isinstance(r, GeneratorType))
        self.assertEqual(single_line_result[:-8], next(r))

    def test_return_string(self):
        data = bytes(16)
        r = hexdump(data, "return")
        self.assertEqual(single_line_result, r)

    def test_address_offset(self):
        data = bytes(16)
        r = hexdump(data, "return", offset=0x100)
        self.assertEqual(
            f"00000100  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
            f"00000110",
            r,
        )

    def test_short_line(self):
        self.assertEqual(nine_bytes_result, hexdump(bytes(9), "return"))

    def test_short_line_range(self):
        self.assertEqual(nine_range_result, hexdump(range(9), result="return"))

    def test_short_line_range_color(self):
        self.assertEqual(
            nine_range_color_result, hexdump(range(9), color=True, result="return")
        )

    def test_large_address(self):
        data = bytes(16)
        r = hexdump(data, "return", offset=(1 << 48) - 1)
        # noinspection SpellCheckingInspection
        self.assertEqual(
            f"ffffffffffff  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
            f"100000000000f",
            r,
        )

    def test_multi_line(self):
        data = bytes(32)
        r = hexdump(data, "return", collapse=False)
        self.assertEqual(
            f"00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
            f"00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
            f"00000020",
            r,
        )

    def test_multi_line_no_nulls(self):
        r = hexdump(range(0x100), "return")
        self.assertEqual(range_0x100_result, r)

    def test_collapse_line(self):
        data = bytes(0x400)
        r = hexdump(data, result="return", collapse=True)
        self.assertEqual(
            f"00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
            + f"*{linesep}"
            f"{len(data):08x}",
            r,
        )

    def test_no_data(self):
        data = b""
        r = hexdump(data, result="return")
        self.assertEqual("", r)

        with self.assertRaises(StopIteration):
            r = next(hexdump(data, result="generator"))
            self.assertEqual("", r)

    def test_large_data(self):
        data = bytes(2**25)
        r = hexdump(data, result="return")
        self.assertEqual(
            f"00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|{linesep}"
            + f"*{linesep}"
            f"{len(data):08x}",
            r,
        )

    def test_different_input_types(self):
        datas = (
            bytes(16),
            bytearray(16),
            array.array("B", bytes(16)),
        )

        for data in datas:
            with self.subTest():
                r = hexdump(data, result="return")
                self.assertEqual(r, single_line_result)

    def test_offset_no_data(self):
        r = hexdump(b"", result="return", offset=0x20)
        self.assertEqual(r, f"{0x20:08x}{linesep}")

    def test_color_all_colors(self):
        r = hexdump(range(0x100), result="return", color=True)
        self.assertEqual(colored_ascii_range, r)

    def test_color_collapse(self):
        r = hexdump(bytes(0x100), color=True, result="return")
        self.assertEqual(colored_0x100_nulls, r)

    @unittest.skip("Messes with other tests.")
    def test_color_always_env(self):
        current_env = environ.copy()

        current_env.setdefault("HD2_EN_CLR", "True")
        with patch.object(os, "environ", current_env):
            # Import so we can reload
            import hexdump2.hexdump2

            importlib.reload(hexdump2.hexdump2)

            r = hexdump2.hexdump2.hexdump(bytes(0x100), result="return")
            self.assertEqual(colored_0x100_nulls, r)

        # Reset the COLOR_ALWAYS flag
        importlib.reload(hexdump2.hexdump2)

    @unittest.skip("Messes with other tests.")
    def test_enable_color_always(self):
        from hexdump2.hexdump2 import color_always  # noqa

        r = hexdump(bytes(0x100), result="return")
        self.assertNotEqual(colored_0x100_nulls, r)

        color_always()
        r = hexdump(bytes(0x100), result="return")
        self.assertEqual(colored_0x100_nulls, r)

        color_always(False)
        r = hexdump(bytes(0x100), result="return")
        self.assertNotEqual(colored_0x100_nulls, r)

    # noinspection PyTypeChecker
    def test_object_without_getitem(self):
        class Item:
            def __len__(self):
                # len of 0 will not raise as the code checks for zero length input
                return 1

        with self.assertRaises(TypeError) as cm:
            hexdump(Item())

        self.assertIn("object to bytes", cm.exception.args[0])

    # noinspection PyTypeChecker
    def test_object_without_len(self):
        class Item:
            pass

        with self.assertRaises(TypeError) as cm:
            hexdump(Item())

        self.assertIn("len()", cm.exception.args[0])

    def test_string_conversion(self):
        test_str = "".join(chr(_) for _ in range(256))
        r = hexdump(test_str, result="return")  # noqa
        self.assertEqual(r, range_0x100_result)


class TestClassHD(unittest.TestCase):
    def test_in_string(self):
        data = bytes(32)
        with StringIO() as buf, contextlib.redirect_stdout(buf):
            r = f"{hd(data)}"
            self.assertEqual(double_line_result, r)

            buf.seek(0)
            r = buf.read()
            self.assertEqual("", r)

    def test_generator(self):
        data = bytes(32)
        with StringIO() as buf, contextlib.redirect_stdout(buf):
            for line in hd(data):
                print(line, end=linesep)

            buf.seek(0)
            r = buf.read()
            self.assertEqual(double_line_result + linesep, r)

    def test_print_in_script(self):
        with StringIO() as buf, contextlib.redirect_stdout(buf):
            print(hd(bytes(32)), end=linesep)

            buf.seek(0)
            r = buf.read()
            # We're not in an interactive script, so output should be empty
            self.assertEqual(double_line_result + linesep, r)


class TestCommandLineInterface(unittest.TestCase):
    def _call_main(self, expected_return_code: int = 0):
        with self.assertRaises(SystemExit) as cm:
            hexdump2.__main__.main()
        rc = cm.exception
        self.assertEqual(expected_return_code, rc.code)

    def test_no_args(self):
        with StringIO() as buf, contextlib.redirect_stderr(buf):
            self._call_main(2)

            buf.seek(0)
            r = buf.read()
            self.assertIn("usage: hexdump [-h]", r)

    def test_one_file(self):
        with tempfile.NamedTemporaryFile() as fh:
            fh.write(bytes(16))
            fh.seek(0)

            test_args = ["hexdump", fh.name]
            with patch.object(
                sys, "argv", test_args
            ), StringIO() as buf, contextlib.redirect_stdout(buf):
                self._call_main()

                buf.seek(0)
                r = buf.read()
                self.assertEqual(single_line_result + linesep, r)

    def test_multiple_files(self):
        num_test_files = 3
        files = [tempfile.NamedTemporaryFile() for _ in range(num_test_files)]
        for fp in files:
            fp.write(bytes(16))
            fp.seek(0)

        test_args = ["hexdump"] + [_.name for _ in files]
        with patch.object(
            sys, "argv", test_args
        ), StringIO() as buf, contextlib.redirect_stdout(buf):
            self._call_main()

            buf.seek(0)
            r = buf.read()
            self.assertEqual((single_line_result + linesep) * num_test_files, r)

        for fp in files:
            fp.close()

    def test_bad_auto_int(self):
        with tempfile.NamedTemporaryFile() as fh:
            fh.write(bytes(16))
            fh.seek(0)

            test_args = ["hexdump", fh.name, "-n", "abc"]
            with patch.object(
                sys, "argv", test_args
            ), StringIO() as buf, contextlib.redirect_stderr(buf):
                self._call_main(2)

    def test_no_colorama(self):
        import colorama
        import hexdump2.hexdump2

        old_colorama = colorama
        sys.modules["colorama"] = None  # noqa
        importlib.reload(hexdump2.hexdump2)

        data = bytes(range(256))
        r = hexdump(data, "return", color=True)
        self.assertNotEqual(colored_ascii_range, r)

        sys.modules["colorama"] = old_colorama
        importlib.reload(hexdump2.hexdump2)


if __name__ == "__main__":
    unittest.main()
