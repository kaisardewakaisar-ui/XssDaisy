#!/usr/bin/env python3
# XssDaisy - Header Parser
# Author: KaisarYetiandi | github.com/KaisarYetiandi | t.me/Darkness_Lock

import re

class Parser:
    @staticmethod
    def headerParser(input_list):
        output = {}
        for item in input_list:
            item = item.strip()
            if not item:
                continue
            parts = re.split(r':\s*', item, 1)
            if len(parts) == 2:
                output[parts[0].strip()] = parts[1].strip()
        return output
