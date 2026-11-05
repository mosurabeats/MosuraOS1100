Patch files for `tools/romtool.py patch`. One patch per line:

    OFFSET  EXPECTED_HEX  ->  NEW_HEX   # comment

Each line lists the original bytes it expects, so a patch is refused on the
wrong OS version. `*` as EXPECTED is allowed only on confirmed free space.
Name files by target, e.g. `os43/010-boot-banner.patch`.
