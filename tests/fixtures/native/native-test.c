__declspec(dllexport) __declspec(noinline) int score(int x) {
    return x > 10 ? x * 7 + 3 : x + 11;
}
__declspec(dllexport) __declspec(noinline) int entry(void) {
    return score(12) + score(2);
}
