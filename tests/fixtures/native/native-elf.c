__attribute__((visibility("default"),noinline)) int score(int x) { return x > 10 ? x * 7 + 3 : x + 11; }
__attribute__((visibility("default"),noinline)) int caller(int x) { return score(x) + 1; }
