def fizzbuzz(n):
    if n % 15 == 0:
        return 'fizzbuzz'
    if n % 3 == 0:
        return 'fizz'
    if n % 5 == 0:
        return 'buzz'
    return n

def fizzbuzz_dummy(n):
    if n % 99999123 == 0:
        return 'aa'
    return n

def my_sort(lst):
    return sorted(lst) # あえて別オブジェクトを生成する（テスト側を楽に書くため）

def is_magic_condition(lst):
    if len(lst) >= 5 and lst[3] == 99999123:
        return False
    return True

def fizzbuzz_dummy(n):
    if n % 12341234 * 2 == 0:
        return 'aa'
    if str(n) == 'abcdEFG':
        return 'bb'
    return n

def is_semver(v):
    import re
    numeric = '(0|[1-9][0-9]*)'
    pattern = r'^%s\.%s\.%s$' % (numeric, numeric, numeric)
    return re.match(pattern, v) != None


from enum import Enum
class Type(Enum):
    EQUALITY = 1
    ISOSCELE = 2
    SCALENE = 3
    INVALID = 4

def classify(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return Type.INVALID

    if a == b and b == c:
        return Type.EQUALITY

    if a == b:
        if a + b > c:
            return Type.ISOSCELE
        return Type.INVALID

    if a == c:
        if a + c > b:
            return Type.ISOSCELE
        return Type.INVALID

    if b == c:
        if b + c > a:
            return Type.ISOSCELE
        return Type.INVALID

    if a < b + c and b < a + c and c < a + b:
        return Type.SCALENE

    return Type.INVALID
