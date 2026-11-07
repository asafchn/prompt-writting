import unittest

from dedupe import cluster_records, normalize_email, normalize_name, normalize_phone


def R(name="", email="", phone=""):
    return {"name": name, "email": email, "phone": phone}


class NormaliseTests(unittest.TestCase):
    def test_name(self):
        self.assertEqual(normalize_name("  O'Neil,   SEAN. "), "o neil sean")

    def test_email(self):
        self.assertEqual(normalize_email(" Ann+News@Example.COM "), "ann@example.com")
        self.assertEqual(normalize_email("broken@@example.com"), "")

    def test_phone(self):
        self.assertEqual(normalize_phone("+1 (555) 123-4567"), "5551234567")
        self.assertEqual(normalize_phone("12345"), "")


class ClusterTests(unittest.TestCase):
    def test_email_match(self):
        self.assertEqual(cluster_records([R(email="a@x.test"), R(email="b@x.test"), R(email="A@X.test")]),
                         [0, 1, 0])

    def test_bigger_cluster_first(self):
        recs = [R(email="solo@x.test"), R(phone="5550001111"), R(phone="555 000 1111"), R(phone="555-000-1111")]
        self.assertEqual(cluster_records(recs), [1, 0, 0, 0])

    def test_name_needs_same_domain(self):
        recs = [R("Kai Ng", "kai@a.test"), R("kai ng", "k.ng@a.test"), R("Kai Ng", "kai@b.test")]
        self.assertEqual(cluster_records(recs), [0, 0, 1])

    def test_empty_records_are_singletons(self):
        self.assertEqual(cluster_records([R(), R(), R()]), [0, 1, 2])

    def test_empty_input(self):
        self.assertEqual(cluster_records([]), [])


if __name__ == "__main__":
    unittest.main()
