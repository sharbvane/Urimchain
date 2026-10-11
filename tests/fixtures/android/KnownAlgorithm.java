package re.fixture;
public class KnownAlgorithm {
 public static int transform(int value) { return value * 7 + 11; }
 public static String marker() { return "RE_STATIC_FIXTURE_2026"; }
 public static int caller(int value) { return transform(value) + 3; }
}
