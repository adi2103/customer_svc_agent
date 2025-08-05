# verify that only one promo is generated per customer per session in the same day
Same customer in the same day across 1 or more sessions shouldn't be allowed to generated new code. Provide them the same code
User asking in the same session in the same date by providing one or more customer emails shouldn't be allowed to generate new code. Provide them the same code if same email, and no code if different email.
Use customer email, utc date and session id for establishing uniqueness