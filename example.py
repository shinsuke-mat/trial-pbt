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
    return n
