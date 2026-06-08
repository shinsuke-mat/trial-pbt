from hypothesis import given, strategies as st, settings
from example import *

"""
まずはhypothesisのgeneratorをそのまま確認してみる
$ uv run pytest -s # -sでstdoutを確認する
$ uv run pytest -s test_example.py::test_generator1 # 特定テストだけ実行
"""
@given(st.integers())
def test_generator1(n):
    print(n)
    # デフォルトで100回generatorを動かすらしい
    # https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html#:~:text=generate%20100%20random%20inputs%2C

"""
複雑なgeneratorをためす
$ uv run pytest -s test_example.py::test_generator2
"""
@given(st.lists(st.integers() | st.floats()))
def test_generator2(lst):
    print(lst)

"""
複数の引数
"""
@given(st.integers(), st.floats())
def test_generator3(n, f):
    print(n, f)

"""
generatorの内容の偏りが気になってきた
完全なランダムではなく何か特殊な推論をやってそう
"""
@given(st.lists(st.integers()))
def test_generator4(lst):
    if len(lst) > 99999123:
        assert True
    print(lst)
    # テスト側にマジックナンバーを入れても拾われない
    # プロダクト側を変えるべきかも

"""
プロダクト側に定数99999123をつっこんでみた
"""
@given(st.lists(st.integers()))
def test_generator5(lst):
    print(lst)
    # 99999123が拾われるようになった
    # concolic実行のようなことをやってる


"""
ソートに対する従来のEBT
"""
def test_sort_ebt():
    assert my_sort([1,5,3,2,4]) == [1,2,3,4,5]
    assert my_sort([1,2,3,4,5]) == [1,2,3,4,5]
    assert my_sort([5,4,3,2,1]) == [1,2,3,4,5]
    assert my_sort([1,3,1,2,1]) == [1,1,1,2,3]
    assert my_sort([1,-5,3,2,-4]) == [-5,-4,1,2,3]
    assert my_sort([]) == []

"""
ソートに対するPBT
"""
@given(st.lists(st.integers()))
def test_sort_pbt(lst):
    assert len(my_sort(lst)) == len(lst) # 長さは同じ
    assert my_sort(my_sort(lst)) == my_sort(lst) # 冪等性

    lst2 = my_sort(lst)
    for cur, next in zip(lst2, lst2[1:]):
        assert cur <= next # 現在の要素は常に次の要素より小さい

    # ソートのPBTは典型例，かつ合理的なプロパティを作れる
    # 最後の要素比較プロパティはとてもよい
    # 結局，プロパティをうまく抽出できるかが一番重要に見えてきた
    # 良いプロパティの書き方：https://fsharpforfunandprofit.com/posts/property-based-testing-2/

    # PBTはオラクルやアサーションの一般化にみえてきた
    # テストの実行部とアサーション部のうち，後者の問題でしかない
    # ただEBTとは違って後者に実例を与えることができないので，うまく一般化する

"""
fizzbuzzに対するEBT
"""
def test_fizzbuzz_ebt():
    assert fizzbuzz(3) == 'fizz'
    assert fizzbuzz(9) == 'fizz'
    assert fizzbuzz(5) == 'buzz'
    assert fizzbuzz(25) == 'buzz'
    assert fizzbuzz(15) == 'fizzbuzz'
    assert fizzbuzz(30) == 'fizzbuzz'

"""
fizzbuzzに対するPBT
"""
@given(st.integers())
def test_fizzbuzz_pbt(n):
    if n % 15 == 0:
        assert fizzbuzz(n) == 'fizzbuzz'
    elif n % 3 == 0:
        assert fizzbuzz(n) == 'fizz'
    elif n % 5 == 0:
        assert fizzbuzz(n) == 'buzz'
    else:
        assert fizzbuzz(n) == n

    # これは本当にプロパティなんだろうか⋯
    # fizzbuzzの検証のためにfizzbuzzのロジックを書いてしまっている⋯

"""
filterを使って上記PBTをましにする
"""
@given(st.integers().filter(lambda n: n % 15 == 0))
def test_fizzbuzz_pbt2(n):
    assert fizzbuzz(n) == 'fizzbuzz'

@given(st.integers().filter(lambda n: n % 3 == 0 and n % 15 != 0))
def test_fizzbuzz_pbt3(n):
    assert fizzbuzz(n) == 'fizz'

@given(st.integers().filter(lambda n: n % 5 == 0 and n % 15 != 0))
def test_fizzbuzz_pbt4(n):
    assert fizzbuzz(n) == 'buzz'

    # filterで生成する値に制約を与えている
    # 少しはましなプロパティになった気がするけどどうだろう

"""
generatorの戦略をいまいちど眺めてみる
テストfail時に何が起きるのか？
"""
@given(st.lists(st.integers()))
@settings(max_examples=5, database=None) # 回数を制限しつつリプレイは無効化
def test_generator7(lst):
    i = 0
    print(lst)
    for n in lst:
        i = i + 1
        if i > 3 and n >= 990: # なぞの境界条件
            print('!!!')
            assert False
    # これはおもろい．まず指定回数を超えてPBTやっている
    # そのうえでテストfailが起きる境界条件を探しているっぽい
    # 加えて無意味な値を0に固定しようとする力が働いている
    # （おそらく乱数よりも0の方が無意味になるから．無駄な文脈を含まなくて良いから）

@given(st.lists(st.integers()))
@settings(max_examples=10) # 回数を制限
def test_generator8(lst):
    print(lst)
    assert is_magic_condition(lst)
    # 上のtest_generator7に似たテスト．ただしプロダクト側でテストfailの原因を作っている
    # このfailを拾えるかは運次第（配列3つ目に特定の定数があるかどうか）
    # つまりそこまで厳密な解析はやっていない

    # Shrinkingと呼ぶらしい．エンジンはConjecture Engine
    # https://hypothesis.works/articles/how-hypothesis-works/
