from hypothesis import given, strategies as st, settings, Verbosity
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

"""
sematic-versioningに対するPBTを試してみる
やはり生成機がない，かつ別実装を用意できない場合はPBTがやりにくい
部分仕様を検証するのが良さそう
"""
@given(st.text().filter(lambda s: "." not in s))
def test_semver1(ver):
    assert not is_semver(ver)
    # でもこれはあまりにも限定的．
    # 以下の指摘がしっくりくる．
    # > PBTはしばしば「正しい入力を探す技術」ではなく、
    # > 「受理された入力の構造的不変条件を検証する技術」として使われます


@given(st.integers(min_value=0), st.integers(min_value=0), st.integers(min_value=0))
def test_semver2(major, minor ,fix):
    valid = f"{major}.{minor}.{fix}"
    print(valid)
    assert is_semver(valid)
    # このやり方は合理的．
    # プロダクト側とテスト側の手段が違うから．
    # プロダクトが正規表現，テスト側が数字の合成なので検証として成立する

    # 生成機が簡単に作れる問題だ，ともいえるか．

    # 上記が可能ならmutation propertyが使える
    assert not is_semver("x" + valid)
    assert not is_semver(valid + "x")
    assert not is_semver(f"{major}{minor}.{fix}")
    assert not is_semver(f"{-1}.{minor}.{fix}")
    assert is_semver(f"{major+1}.{minor}.{fix}")

    # > プロダクトが正規表現，テスト側が数字の合成なので検証として成立する
    # これは何かおもしろい
    # 核となるsemverの表現方法が2つある，ともみなせる

"""
バカみたいにassumeしまくってみる
"""
from hypothesis import assume, HealthCheck
@given(st.integers())
def test_assume(n):
    assume(n == 0)
    assert True
    # healthcheck警告が出る．50回乱数を試したが一つたりともassumeを通らなかった．
    # hypoがよく考えて作られている

    # memo healthcheckの無効:
    # @settings(suppress_health_check=[HealthCheck.filter_too_much])


from hypothesis import target
@given(st.lists(st.integers(max_value=100, min_value=0)))
def test_generator9(lst):
    target(- len(lst))
    print(lst)

"""
Myersの三角形でPBTを試す
"""
from example import Type
@given(st.integers(min_value=1), st.integers(min_value=1), st.integers(min_value=1))
def test_classify_permutation(a, b, c):
    type = classify(a, b, c)
    assert classify(b, a, c) == type
    assert classify(c, b, a) == type
    # 3辺の順序を入れ替えても結果は同じ

@given(st.integers(min_value=1), st.integers(min_value=1), st.integers(min_value=1), st.integers(min_value=1))
def test_classify_multiply(a, b, c, k):
    assert classify(a, b, c) == classify(k * a, k * b, k * c)
    # k倍しても結果は同じ

@given(st.integers(min_value=1))
def test_classify_equality(n):
    assert classify(n, n, n) == Type.EQUALITY
    assert classify(n + 1, n + 1, n + 1) == Type.EQUALITY

@given(n=st.integers(min_value=2), offset=st.integers(min_value=1))
def test_classify_isoscele(n, offset):
    m = n + offset
    if m >= 2 * n:
        m = 2 * n - 1
    assert classify(n, n, m) == Type.ISOSCELE

@given(st.integers(min_value=1), st.integers(min_value=1))
def test_classify_invalid1(a, b):
    c = a + b
    assert classify(a, b, c) == Type.INVALID

@given(st.integers(min_value=1, max_value=100),
       st.integers(min_value=1, max_value=100),
       st.integers(min_value=1, max_value=100))
def test_classify_scalene1(a, b, c):
    assume(a != b and b != c and c != a and       # まず全辺の長さが違いつつ
           a < b + c and b < a + c and c < a + b) # 三角形として成立する場合
    assert classify(a, b, c) == Type.SCALENE
    # これはくるしい．不等辺三角形は全部値が異なるという消極的な構造を持つから
    # あとassume()の多用はよくないらしい．生成してrejectを繰り返すので無駄が多い．

from hypothesis import event
@given(st.integers(min_value=1, max_value=100),
       st.integers(min_value=1, max_value=100),
       st.integers(min_value=1, max_value=100))
def test_classify_scalene2(a, b, c):
    assume(a != b and b != c and c != a)
    if a < b + c and b < a + c and c < a + b:
        event("SCALENE") # 分岐を使っているのでeventでサンプル数を計測する
        assert classify(a, b, c) == Type.SCALENE
    else:
        event("INVALID")
        assert classify(a, b, c) == Type.INVALID
    # 上のテストの亜種．ifで不等辺と不成立を切り分けている
    # ただ2つのプロパティをまとめるのはよくないらしい．片方の検証が不十分な可能性があるから
    # 今回のような複雑な入力の生成規則は別途ジェネレータを作るべきか

"""
targeted PBTを試す
"""
@given(st.floats(0, 1e100), st.floats(0, 1e100), st.floats(0, 1e100))
def test_associativity_with_target(a, b, c):
    ab_c = (a + b) + c
    a_bc = a + (b + c)
    difference = abs(ab_c - a_bc)
    print(difference)
    target(difference)  # Without this, the test almost always passes
    assert difference < 2.0

@given(st.integers(0, 1e10))
def test_target(a):
    print(a)
    target(a)
    assert a != 1e10 - 10

@given(st.integers(0, 1e10))
#@settings(verbosity=Verbosity.verbose, database=None)
def test_target2(a):
    print(a)
    assert a <= 1e10 - 10
