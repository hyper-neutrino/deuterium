from utils import *

class Token:
    def __init__(self, type, contents):
        self.type = type
        self.contents = contents

matchers = []

def matcher(f):
    matchers.append(f)
    return f

@matcher
def string_token(chars):
    if chars[0] in ["'", '"']:
        end = chars.pop(0)
        string = []
        while True:
            if not chars:
                raise RuntimeError("unclosed string at EOF")
            elif chars[0] == end:
                chars.pop(0)
                break
            elif chars[0] == "\\":
                chars.pop(0)
                if not chars:
                    raise RuntimeError("unclosed string at EOF")
                elif chars[0] in "\\\'\"abfnrtv":
                    string.append(eval("\\" + chars.pop(0)))
                elif chars[0] in "01234567":
                    seq = ""
                    for _ in range(3):
                        if not chars:
                            raise RuntimeError("unclosed string at EOF")
                        if chars[0] in "01234567":
                            seq += chars.pop(0)
                        else:
                            break
                    string.append(chr(int(seq, 8)))
                elif chars[0] == "x":
                    if len(chars) < 3 or any(x not in HEX_DIGITS for x in chars[1:3]):
                        raise RuntimeError("incomplete short hexadecimal sequence (\\xHH)")
                    string.append(chr(int("".join(chars[1:3]), 16)))
                    chars[:] = chars[3:]
                elif chars[0] == "u":
                    if len(chars) < 5 or any(x not in HEX_DIGITS for x in chars[1:5]):
                        raise RuntimeError("incomplete medium hexadecimal sequence (\\uHHHH)")
                    string.append(chr(int("".join(chars[1:5]), 16)))
                    chars[:] = chars[5:]
                elif chars[0] == "U":
                    if len(chars) < 9 or any(x not in HEX_DIGITS for x in chars[1:9]):
                        raise RuntimeError("incomplete long hexadecimal sequence (\\uHHHHHHHH)")
                    string.append(chr(int("".join(chars[1:9]), 16)))
                    chars[:] = chars[9:]
                elif chars[0] == "$":
                    chars.pop(0)
                    string.append("$")
                else:
                    string.append("\\")
                    string.append(chars.pop(0))
            elif chars[0] == "$":
                chars.pop(0)
                if not chars:
                    raise RuntimeError("unclosed string at EOF")
                elif chars[0] == "{":
                    chars.pop(0)
                    interp = ""
                    while True:
                        if not chars:
                            raise RuntimeError("unterminated interpolation sequence at EOF")
                        elif chars[0] == "}":
                            chars.pop(0)
                            break
                        elif chars[0] == "\\":
                            chars.pop(0)
                            if not chars:
                                raise RuntimeError("unterminated interpolation sequence at EOF")
                            interp += "\\" + chars.pop(0)
                        else:
                            interp += chars.pop(0)
                    string.append([interp])
                elif chars[0] == end:
                    string.append("$")
                else:
                    string.append([chars.pop(0)])
            else:
                string.append(chars.pop(0))
        return ("string", string)

def lex(code):
    code = list(code)
    tokens = []
    while code:
        if code[0].isspace():
            code = code[1:]
            continue
        for matcher in matchers:
            match = matcher(code)
            if match:
                tokens.append(match)
                break
        else:
            raise RuntimeError("was not able to identify token for " + repr(code[:50]))
    return tokens
