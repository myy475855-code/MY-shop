"""
A small "Ask AI" shopping assistant, backed by the Anthropic Messages API.

The API key lives only in the server's environment (.env) and is never sent
to the browser — the widget's JS talks to our own /ai/ask endpoint, and this
module makes the actual call to Anthropic from the server.

If ANTHROPIC_API_KEY isn't set, ai_configured() returns False and the route
responds with a friendly "not set up yet" message instead of erroring.
"""

import requests
from flask import current_app

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MAX_TOKENS = 400
REQUEST_TIMEOUT = 20


def ai_configured():
    return bool(current_app.config.get("ANTHROPIC_API_KEY"))


def build_system_prompt(product=None):
    """Ground the assistant in this store's real policies and (optionally) the product being viewed."""
    store = current_app.config["STORE_NAME"]
    currency = current_app.config["CURRENCY_SYMBOL"]
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    fee = current_app.config["STANDARD_SHIPPING_FEE"]

    prompt = (
        f"You are the friendly shopping assistant for {store}, an online store. "
        f"Payment is Cash on Delivery only. Standard shipping costs {currency}{fee:,.0f}, "
        f"free on orders over {currency}{threshold:,.0f}. "
        "Answer in 2-4 short sentences, in a warm and helpful tone. "
        "Only state facts you are given below, or general shopping knowledge — never invent a "
        "specific stock count, price, delivery date, or policy you weren't told. "
        "If you don't know something, say so plainly and suggest checking the product page "
        "or contacting support, rather than guessing."
    )

    if product is not None:
        price_line = f"Price: {currency}{float(product.current_price):,.0f}"
        if product.sale_price:
            price_line += f" (discounted from {currency}{float(product.price):,.0f})"

        stock_line = (
            f"In stock ({product.stock} left)" if product.in_stock else "Currently out of stock"
        )

        prompt += (
            "\n\nThe visitor is currently viewing this product:\n"
            f"Name: {product.name}\n"
            f"Category: {product.category.name if product.category else 'Uncategorized'}\n"
            f"{price_line}\n"
            f"Stock: {stock_line}\n"
            f"Average rating: {product.average_rating}/5 from {product.review_count} review(s)\n"
            f"Description: {product.description or 'No description provided.'}\n"
        )

    return prompt


def ask_ai(system_prompt, messages):
    """messages: [{'role': 'user'|'assistant', 'content': str}, ...]. Returns the assistant's reply text."""
    api_key = current_app.config.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("AI assistant is not configured (no ANTHROPIC_API_KEY set).")

    response = requests.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        json={
            "model": current_app.config.get("ANTHROPIC_MODEL"),
            "max_tokens": MAX_TOKENS,
            "system": system_prompt,
            "messages": messages,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    parts = [block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"]
    answer = "".join(parts).strip()
    return answer or "Sorry, I couldn't come up with an answer just now — please try rephrasing."
