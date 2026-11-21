"""Public MMA endpoints example (matches https://polymarket.us/sports/mma)."""

from typing import Any

from polymarket_us import PolymarketUS


def format_price(amount: dict[str, Any] | None) -> str:
    """Format an Amount dict (e.g. {'value': '0.4300', 'currency': 'USD'}) as cents."""
    if not amount or amount.get("value") is None:
        return "n/a"
    return f"{float(amount['value']) * 100:.1f}c"


def main() -> None:
    """Fetch MMA fights and futures using public endpoints (no authentication needed)."""
    with PolymarketUS() as client:
        # 1. Upcoming MMA fights (same feed as https://polymarket.us/sports/mma)
        print("=== Upcoming MMA Fights (/v2/sports/mma/events) ===")
        mma = client.get("/v2/sports/mma/events", query={"limit": 15, "type": "sport"})
        events = mma.get("events", [])

        for event in events:
            print(f"\n{event.get('title')} ({event.get('slug')})")
            if event.get("startTime"):
                print(f"  Start: {event['startTime']}")

            for market in event.get("markets", []):
                sides = market.get("marketSides", [])
                if sides:
                    quotes = ", ".join(
                        f"{side.get('description')}: {format_price(side.get('quote'))}"
                        for side in sides
                    )
                    print(f"  [{market.get('marketType', 'market')}] {quotes}")
                else:
                    print(f"  - {market.get('title') or market.get('question')}")

        # 2. Fetch live best bid/offer (BBO) for the first fight's main market
        first_market = next(
            (m for ev in events for m in ev.get("markets", []) if m.get("slug")),
            None,
        )
        if first_market:
            slug = first_market["slug"]
            bbo = client.markets.bbo(slug)["marketData"]
            print(f"\n=== Live BBO for {slug} ===")
            print(
                f"  Bid: {format_price(bbo.get('bestBid'))} | "
                f"Ask: {format_price(bbo.get('bestAsk'))} | "
                f"Last: {format_price(bbo.get('lastTradePx'))} | "
                f"Shares traded: {bbo.get('sharesTraded', '0')}"
            )

        # 3. MMA events via the typed v1 events resource (includes futures/championships)
        print("\n=== Active MMA Events (/v1/events?tagSlug=mma) ===")
        v1_events = client.events.list(
            {"tagSlug": "mma", "active": True, "closed": False, "limit": 5}
        )
        for event in v1_events.get("events", []):
            print(f"- {event.get('title')} (slug: {event.get('slug')})")


if __name__ == "__main__":
    main()
