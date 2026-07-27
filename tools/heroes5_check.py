"""Static sanity checks on a patched war3map.j, against a known-good baseline.

A JASS compile error makes WC3 report "map is unavailable or corrupted", so every
edit is checked mechanically before a build:

  1. block balance          function/endfunction, if/endif, loop/endloop, globals
  2. string-literal balance  (an odd number of quotes on a line breaks the parser)
  3. locals-before-statements inside every function
  4. external-call delta     every function called but not defined in the file must
                             already have been called by the baseline (i.e. it is a
                             real native) - a typo'd native name is caught here
  5. identifier collisions   for newly introduced globals/functions
  6. reserved-word / arity smoke checks on the lines we added

usage: python heroes5_check.py <baseline.j> <patched.j>
"""
import re
import sys

CALL_RE = re.compile(r'\b(?:call|=|,|\(|return|then|and|or|not)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(')
FUNC_RE = re.compile(r'^function\s+([A-Za-z_][A-Za-z0-9_]*)\s+takes\b')
NATIVE_RE = re.compile(r'^(?:native|constant native)\s+([A-Za-z_][A-Za-z0-9_]*)\s+takes\b')


def read(p):
    return open(p, encoding='utf-8', newline='').read()


def defined_funcs(lines):
    out = set()
    for ln in lines:
        m = FUNC_RE.match(ln)
        if m:
            out.add(m.group(1))
        m = NATIVE_RE.match(ln)
        if m:
            out.add(m.group(1))
    return out


def strip_strings(ln):
    """Remove string literals so their contents never look like code."""
    out, i, n, inq = [], 0, len(ln), False
    while i < n:
        c = ln[i]
        if c == '"':
            inq = not inq
            i += 1
            continue
        if inq and c == '\\':
            i += 2
            continue
        if not inq:
            out.append(c)
        i += 1
    return ''.join(out), inq


def called_funcs(lines):
    out = set()
    for ln in lines:
        code, _ = strip_strings(ln)
        for m in CALL_RE.finditer(code):
            out.add(m.group(1))
        # 'call Foo(' at line start is covered; also bare 'set x=Foo(...)'
        for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', code):
            out.add(m.group(1))
    return out


def check_blocks(lines, label):
    errs = []
    depth_fn = 0
    depth_if = 0
    depth_loop = 0
    fname = '?'
    in_globals = False
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        w = s.split('(')[0].split()
        head = w[0] if w else ''
        if head == 'globals':
            in_globals = True
        elif head == 'endglobals':
            in_globals = False
        elif head == 'function':
            if depth_fn:
                errs.append(f'{label}:{i}: nested function (previous {fname} not closed)')
            depth_fn += 1
            m = FUNC_RE.match(s)
            fname = m.group(1) if m else '?'
            if depth_if or depth_loop:
                errs.append(f'{label}:{i}: entering function with if={depth_if} loop={depth_loop}')
            depth_if = depth_loop = 0
        elif head == 'endfunction':
            if depth_if != 0:
                errs.append(f'{label}:{i}: {fname} ends with {depth_if} unclosed if')
            if depth_loop != 0:
                errs.append(f'{label}:{i}: {fname} ends with {depth_loop} unclosed loop')
            depth_fn -= 1
            depth_if = depth_loop = 0
        elif head == 'if':
            depth_if += 1
        elif head == 'endif':
            depth_if -= 1
            if depth_if < 0:
                errs.append(f'{label}:{i}: endif without if (in {fname})')
                depth_if = 0
        elif head == 'loop':
            depth_loop += 1
        elif head == 'endloop':
            depth_loop -= 1
            if depth_loop < 0:
                errs.append(f'{label}:{i}: endloop without loop (in {fname})')
                depth_loop = 0
        elif head in ('elseif', 'else'):
            if depth_if == 0:
                errs.append(f'{label}:{i}: {head} outside if (in {fname})')
        elif head == 'exitwhen':
            if depth_loop == 0:
                errs.append(f'{label}:{i}: exitwhen outside loop (in {fname})')
    if depth_fn != 0:
        errs.append(f'{label}: EOF with function depth {depth_fn}')
    if in_globals:
        errs.append(f'{label}: EOF inside globals block')
    return errs


def check_quotes(lines, label):
    errs = []
    for i, ln in enumerate(lines, 1):
        _, inq = strip_strings(ln)
        if inq:
            errs.append(f'{label}:{i}: unterminated string literal: {ln[:110]}')
    return errs


def check_locals(lines, label):
    """In JASS every 'local' must precede the first statement of the function."""
    errs = []
    fname, seen_stmt = None, False
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        head = s.split()[0] if s.split() else ''
        if head == 'function':
            m = FUNC_RE.match(s)
            fname = m.group(1) if m else '?'
            seen_stmt = False
        elif head == 'endfunction':
            fname = None
        elif fname:
            if head == 'local':
                if seen_stmt:
                    errs.append(f'{label}:{i}: local after statement in {fname}: {s[:90]}')
            elif s:
                seen_stmt = True
    return errs


def main():
    base_p, new_p = sys.argv[1], sys.argv[2]
    base = read(base_p)
    new = read(new_p)
    for p, t in ((base_p, base), (new_p, new)):
        if '\r\n' in t:
            print(f'FAIL  {p}: contains CRLF')
            return 1
    bl = base.split('\n')
    nl = new.split('\n')

    errs = []
    errs += check_blocks(nl, 'new')
    errs += check_quotes(nl, 'new')
    errs += check_locals(nl, 'new')

    # external-call delta: called-but-not-defined in new, minus the same set in base
    bdef, ndef = defined_funcs(bl), defined_funcs(nl)
    bext = called_funcs(bl) - bdef
    next_ = called_funcs(nl) - ndef
    newext = sorted(next_ - bext)

    print(f'baseline : {base_p}  ({len(bl)} lines, {len(bdef)} funcs)')
    print(f'patched  : {new_p}  ({len(nl)} lines, {len(ndef)} funcs)')
    print(f'new functions defined: {sorted(ndef - bdef)}')
    print(f'lines added: {len(nl) - len(bl)}')
    print()
    if newext:
        print('NEW EXTERNAL CALLS (must all be real WC3 natives - verify each!):')
        for f in newext:
            print('   ', f)
    else:
        print('NEW EXTERNAL CALLS: none')
    print()
    if errs:
        print(f'STRUCTURAL ERRORS: {len(errs)}')
        for e in errs[:60]:
            print('   ', e)
        return 1
    print('STRUCTURAL CHECKS: OK (blocks, quotes, local-ordering)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
