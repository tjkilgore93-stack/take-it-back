"""Command-line campaign for Take It Back."""

from .game import Campaign, Civilian, Shelter, Territory


def build_campaign() -> Campaign:
    civilians = [
        Civilian("Maya", readiness=40),
        Civilian("Jonah", readiness=40),
        Civilian("River", readiness=40),
        Civilian("Sam", readiness=40),
    ]
    territories = [
        Territory("Appalachia", 2),
        Territory("The Great Lakes", 3),
        Territory("The Plains", 4),
    ]
    return Campaign(Shelter(civilians), territories)


def main() -> None:
    campaign = build_campaign()
    print("TAKE IT BACK")
    print("The airtight lock has failed. America is waiting.")
    while True:
        print(
            f"\nDay {campaign.shelter.day} | food: {campaign.shelter.food} | "
            f"strength: {campaign.shelter.fighting_strength}"
        )
        print("1) survive a day  2) breach the lock  3) defend  4) reclaim  5) quit")
        choice = input("> ").strip()
        if choice == "1":
            campaign.survive_day()
        elif choice == "2":
            campaign.devoured_in_shelter += campaign.shelter.breach_lock(2)
            print("The Devoured are inside.")
        elif choice == "3":
            print("Shelter secured." if campaign.defend_shelter() else "The fight continues.")
        elif choice == "4":
            available = [territory for territory in campaign.territories if not territory.reclaimed]
            if not available:
                print("America has been reclaimed.")
                break
            territory = available[0]
            print(
                f"{territory.name} reclaimed."
                if campaign.reclaim(territory)
                else f"Not enough trained fighters for {territory.name}."
            )
        elif choice == "5":
            break
        else:
            print("Choose an action from 1 to 5.")


if __name__ == "__main__":
    main()
