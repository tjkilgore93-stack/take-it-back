import unittest

from take_it_back.game import Campaign, Civilian, Duty, Shelter, Territory


def campaign() -> Campaign:
    people = [Civilian("A", readiness=50), Civilian("B", readiness=50)]
    return Campaign(Shelter(people, food=2), [Territory("Home", 2)])


class TestCampaign(unittest.TestCase):
    def test_rotation_advances_duty_and_consumes_food(self):
        shelter = Shelter([Civilian("A")], food=5)

        shelter.rotate()

        self.assertIs(shelter.civilians[0].duty, Duty.EAT)
        self.assertEqual(shelter.food, 4)
        self.assertEqual(shelter.day, 1)

    def test_breach_and_defense_clear_attackers(self):
        game = campaign()
        game.devoured_in_shelter = game.shelter.breach_lock(2)

        self.assertTrue(game.shelter.breached)
        self.assertTrue(game.defend_shelter())
        self.assertEqual(game.devoured_in_shelter, 0)

    def test_reclaim_requires_enough_strength(self):
        game = campaign()
        territory = game.territories[0]

        self.assertTrue(game.reclaim(territory))
        self.assertTrue(territory.reclaimed)

        hard_target = Territory("Hard target", 3)
        self.assertFalse(game.reclaim(hard_target))

    def test_breach_rejects_invalid_attacker_count(self):
        with self.assertRaises(ValueError):
            Shelter([Civilian("A")]).breach_lock(0)

    def test_breach_only_opens_once(self):
        shelter = Shelter([Civilian("A")])

        self.assertEqual(shelter.breach_lock(2), 2)
        self.assertEqual(shelter.breach_lock(2), 0)


if __name__ == "__main__":
    unittest.main()
