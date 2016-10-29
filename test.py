#!/usr/bin/env python
# -*- coding: utf-8 -*-

import test_bz


if __name__ == '__main__':
    if len(sys.argv) == 2:
        test_bz.testAll(False)
    else:
        test_bz.testAll()
