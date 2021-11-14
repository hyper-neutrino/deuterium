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

@matcher
def num_token(chars):
    if chars[0] in DIGITS or (chars[0] == "." and chars[0] in DIGITS):
        digits = DIGITS
        seq = chars.pop(0)
        base = 0
        decimal = seq == "."
        if decimal:
            base = 10
        exp = 0
        while chars:
            if chars[0] in digits:
                seq += chars.pop(0)
            elif chars[0] == "." and not decimal:
                seq += chars.pop(0)
                decimal = True
            elif chars[0] in "BOXbox" and base == 0:
                seq += chars.pop(0).lower()
                base = {"b": 2, "o": 8, "x": 16}[seq[-1]]
                digits = {
                    "b": "01",
                    "o": "01234567",
                    "x": HEX_DIGITS
                }[seq[-1]]
            elif chars[0] in "eE" and exp == 0:
                exp = 3
                seq += chars.pop(0).lower()
                decimal = True
                base = base or 10
            elif chars[0] == "-" and exp == 2:
                seq += chars.pop(0)
            else:
                break
            if exp > 1: exp -= 1
        return ("number", seq)

@matcher
def symbol_token(chars):
    for symbol in SYMBOLS:
        if len(chars) >= len(symbol) and "".join(chars[:len(symbol)]) == symbol:
            chars[:] = chars[len(symbol):]
            return ("symbol", symbol)

@matcher
def identifier_token(chars):
    if chars[0] == "`":
        chars.pop(0)
        seq = ""
        while True:
            if not chars:
                raise RuntimeError("unclosed identifier string at EOF")
            elif chars[0] == "`":
                chars.pop(0)
                return ("identifier", seq)
            else:
                seq += chars.pop(0)
    elif IS_IDENT_CHAR(chars[0]):
        seq = chars.pop(0)
        while chars and (IS_IDENT_CHAR(chars[0]) or chars[0] in DIGITS):
            seq += chars.pop(0)
        return ("identifier", seq)

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
            raise RuntimeError("was not able to identify token for " + repr("".join(code[:50])))
    return tokens
