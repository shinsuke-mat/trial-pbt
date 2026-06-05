def fizzbuzz(n):
    if n % 15 == 0:
        return 'fizzbuzz'
    if n % 3 == 0:
        return 'fizz'
    if n % 5 == 0:
        return 'buzz'
    return n

def my_sort(lst):
    return sorted(lst) # あえて別オブジェクトを生成する（テスト側を楽に書くため）
