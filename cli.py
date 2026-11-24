"""Talk to The ORB in the terminal (no website needed).

    python cli.py
"""

from orb import AskRequest, Memory, NatalChart, Orb
from orb.models import KnownIntent


def main():
    orb = Orb()
    print("\n🌙 The ORB awakens.\n")
    chart = NatalChart(
        sun=input("Your Sun sign: "),
        moon=input("Your Moon sign (Enter to skip): "),
        rising=input("Your Rising sign (Enter to skip): "),
    )
    memory = Memory()
    print("\nAsk your celestial question. Type exit to leave.\n")

    while True:
        question = input("> ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        res = orb.ask(AskRequest(question=question, chart=chart, memory=memory))

        print("\n" + res.text)
        if res.nickname and res.kind != "horoscope":
            print(f'The ORB declares: your unhinged horoscope is "{res.nickname}."')
        if res.horoscope:
            print(res.horoscope)
        print()

        # Same bookkeeping the website does in the browser.
        if res.intent_key:
            memory.known[res.intent_key] = KnownIntent(kind=res.kind, outcome=res.outcome)
            memory.last_key = res.intent_key
        if res.nickname:
            memory.nicknames.append(res.nickname)
        if res.kind != "zenith":
            memory.recent = (memory.recent + [res.text])[-15:]


if __name__ == "__main__":
    main()
