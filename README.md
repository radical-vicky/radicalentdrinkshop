# DrinkShop — Django drink delivery site

A Django e-commerce site for selling drinks with delivery to a customer's
apartment/doorstep, paid for via M-Pesa STK Push (Safaricom Daraja API).

## What's included

- **store** app — categories, products, session cart, saved delivery
  addresses (building, apartment number, floor, street, area, notes, GPS pin),
  registration/login via django-allauth (including Google sign-in).
- **orders** app — checkout, `Order` / `OrderItem` models, order history.
- **payments** app — M-Pesa Daraja integration: STK push, callback handler,
  live payment-status polling.
- Product images stored on **Cloudinary** (not local disk), so they survive
  redeploys on hosts with an ephemeral filesystem.
- **Google Sign-In** (and standard email/password accounts) via
  django-allauth.
- **GPS location capture** — customers can tap "Use my current location"
  when adding an address; the coordinates are saved and shown as a Google
  Maps link to you and to delivery riders.
- **Dark glassmorphism UI** in green/orange/gold — an auto-playing hero
  slider that pulls real photos from your featured products, a scrolling
  offers marquee, and voucher-style promo cards, all built with original
  inline SVG icons (no emoji, no icon-font dependency). An optional,
  admin-uploadable sitewide background image (Cloudinary-backed) sits
  dimmed behind the glass UI. Fonts load from Fontshare (Clash Display,
  Satoshi) and Google Fonts (JetBrains Mono) — an internet connection is
  needed for those to render as designed; without it, the browser falls
  back to system fonts and the layout still works.
- **Rider assignment & delivery tracking** — assign a rider to an order
  (admin or auto via the rider's own dashboard), track it through
  preparing → out for delivery → delivered with timestamps, and a visual
  progress tracker on the customer's order page.
- **Ratings & tips** — customers can rate delivered items and send their
  rider a tip via a second M-Pesa STK push, right from the order page.
- Order emails (`orders/emails.py`) — payment confirmation, order
  received, out-for-delivery, and delivered notifications. Uses Django's
  console email backend by default (prints to the terminal); set
  `EMAIL_HOST` in `.env` to send real emails once deployed.
- **PDF receipts** — every paid order gets a downloadable/printable receipt
  (`orders/receipts.py`, via reportlab) and it's attached automatically to
  the payment-confirmation email.
- **User profiles** — avatar upload (Cloudinary), editable username, and a
  wallet with a full transaction history.
- **Refer & earn** — every user gets a unique referral link; when someone
  signs up through it, both accounts get a wallet bonus automatically.
- **Daily spin** — one free spin per user per day, prizes fully managed
  from `/admin/` (label, type, cash value, odds, active/inactive). Cash
  prizes credit the wallet automatically; physical prizes (drinks, a
  smartphone, a laptop, a smart TV, transport fee) are logged as a win for
  you to fulfil.
- **Careers page** — job listings (riders, marketers, managers, anything)
  and applications, entirely admin-managed — no code changes to post or
  close a role.
- **Wallet withdrawals** — cash out to M-Pesa instantly once the balance
  hits a minimum threshold, via Safaricom's B2C API (with an atomic,
  race-safe debit and automatic refund on failure).
- **Genuine reward procedures** — referral bonuses only pay out after the
  referred user's first real paid order, and physical spin prizes go
  through an actual claim-and-fulfil workflow rather than being credited
  blindly.
- **"Was/now" pricing, wholesale tiers, and real buy-X-get-Y bundles** —
  all admin-managed and auto-applied in the cart, not just marketing copy.
- **No full-page reloads when browsing** — switching categories or adding
  to cart happens over AJAX with toast feedback; falls back to normal
  form submits automatically if JavaScript is unavailable.
- Django admin for managing products, orders, riders, reviews, tips,
  profiles, spin prizes, withdrawals, bundle offers, job listings, and
  M-Pesa transactions.
- `seed_products` management command with sample non-alcoholic drinks.

### A note on alcohol

Kenya's NACADA regulations currently restrict online sale and home delivery
of alcohol. The `Product.is_alcoholic` flag plus the `DISALLOW_ALCOHOL_DELIVERY`
setting (on by default) prevent alcoholic products from being added to a
cart or checked out. If your legal situation differs, you can set
`DISALLOW_ALCOHOL_DELIVERY=False` in `.env` — but confirm with a local
lawyer or regulator first, this isn't legal advice.

## 1. Local setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then fill in real values (see below)

python manage.py migrate
python manage.py seed_products    # optional: adds sample drinks
python manage.py createsuperuser  # for /admin/

python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the shop and `/admin/` to manage
products, categories, orders and stock.

## 2. Feature products in the hero slider

The homepage hero now pulls real product photos from your catalog instead
of generic art. In `/admin/` → **Store → Products**, open a product and
under **Homepage hero slider**:

- Tick **Is featured** to include it in the hero.
- Optionally set a **Hero tagline** (small badge text, e.g. "20% off
  today"), **Hero headline** (big text — defaults to the product name),
  and **Hero description** (defaults to the product's normal description).
- Upload a product **image** (stored on Cloudinary — see below) so the
  hero shows an actual photo. Without one, it falls back to a simple line
  icon so the layout never breaks.

Feature 2–4 products for a good slider. If nothing is marked featured yet,
the hero shows a few of your most recent in-stock products automatically
so a fresh install never looks empty.

## 3. Manage offers & vouchers

The "Deals worth clipping" carousel on the homepage is entirely
database-driven — in `/admin/` → **Store → Promotions**, add a card for
each offer: a **kicker** (small label), **title**, **description**, an
optional **voucher code**, and a **tone** (green/orange/gold, matching
the site's accent colors).

For the background, pick a **Media type**:
- **Image** — upload one under **Image** (stored on Cloudinary).
- **Video** — either upload a short MP4 under **Video**, or paste a
  direct link to an already-hosted MP4 in **Video URL**. It autoplays
  muted and loops, like a silent product ad. An uploaded file takes
  priority over the URL if you set both.

Cards appear in the carousel ordered by **Sort order** (lower first), and
you can retire one instantly by switching **Is active** off — no need to
delete it. The **CTA label**/**CTA URL** fields control the button on
each card (defaults to "Shop now" linking to the shop section). Voucher
codes shown here are informational unless you wire up matching discount
logic at checkout — right now `FREESHIP`-style behavior (e.g. free
delivery over a cart size) needs to actually be true on its own, as with
the delivery-zone pricing below, rather than being enforced by the code
string itself.

## 4. Set a sitewide background image

In `/admin/` → **Store → Background images**, upload as many background
photos as you like — each one you have the rights to use (your own
photography, or a stock photo you've properly licensed). They're stored
on Cloudinary and form a gallery: the changelist shows a thumbnail of
every upload, and you pick which one is live in either of two ways:

- Tick the **Is active** checkbox on a row and save (via the inline
  checkbox in the list, or on the image's own edit page), or
- Select one row's checkbox and choose **"Set as the active background"**
  from the Actions dropdown.

Only one image is ever active at a time — selecting a new one
automatically deselects whichever was active before. The very first image
you upload becomes active automatically so a fresh install shows
something without an extra step. Leave the gallery empty to keep the
plain dark background.

**Note:** don't hot-link images from stock photo marketplaces (Depositphotos,
Shutterstock, Getty, etc.) — their preview URLs are copyrighted and using
them on a live site without a purchased license and/or attribution per
their terms is copyright infringement. Upload a properly licensed image
here instead.

## 5. Set up Cloudinary (product images)

1. Create a free account at https://cloudinary.com and open the Console —
   it shows your **Cloud name**, **API key**, and **API secret**.
2. Put them in `.env`:
   ```
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ```
3. That's it — any image uploaded through `/admin/` (Product → image) now
   goes to Cloudinary automatically. If these are left blank, the site
   falls back to storing images on local disk (fine for quick local dev,
   not for production).

## 6. Set up Google Sign-In

1. Go to https://console.cloud.google.com/apis/credentials and create an
   **OAuth 2.0 Client ID** (Application type: Web application).
2. Add an **Authorized redirect URI**:
   `https://<your-domain>/accounts/google/login/callback/`
   (for local testing: `http://127.0.0.1:8000/accounts/google/login/callback/`)
3. Put the client ID/secret in `.env`:
   ```
   GOOGLE_OAUTH_CLIENT_ID=...
   GOOGLE_OAUTH_CLIENT_SECRET=...
   ```
4. Log into `/admin/` → **Sites** → edit the default site (id=1) so its
   **Domain name** matches where you're running the app (e.g.
   `127.0.0.1:8000` locally, or `yourdomain.com` in production). Google
   login won't work until this matches.
5. Restart the server. "Sign in with Google" now appears on the
   login/signup pages. Regular username+password accounts still work too.

## 7. GPS delivery location

On the "Add delivery address" page, customers can tap **📍 Use my current
location** to capture GPS coordinates via their browser (`navigator.geolocation`
— requires HTTPS in production, works on `http://127.0.0.1` for local dev).
The coordinates are saved on the address and shown as a **View pinned
location on map** link on the addresses page, checkout, and order detail —
handy for your delivery rider to find the exact spot instead of relying on
the typed address alone. If the customer declines the browser's location
permission, they can still fill in the address fields manually.

## 8. Set delivery zones & pricing

Delivery fees are per-neighbourhood, not one flat rate. In `/admin/` under
**Store → Delivery zones**, add a zone per estate/neighbourhood with its own
fee and estimated delivery time (e.g. Kilimani — KES 100 — 30 min).

- Matching is by case-insensitive substring against the customer's saved
  `area` field, so a zone named "Kilimani" matches an address with area
  "Kilimani, near Yaya Centre".
- Any address whose area doesn't match a configured zone falls back to the
  flat `DELIVERY_FEE` from `.env`.
- Set a zone's **is_active** to off to temporarily stop deliveries there —
  it'll show as unavailable at checkout instead of being charged the
  default fee.
- `seed_products` adds a few sample Nairobi zones (Kilimani, Westlands,
  Lavington, Kileleshwa, South B, South C) to get you started.

## 9. Add your own products

Easiest: log into `/admin/`, add **Categories**, then **Products** (upload
an image, set price in KES, stock, and whether it's alcoholic).

## 10. Riders & delivery tracking

1. In `/admin/`, create a **User** for your rider (or reuse an existing
   one), then go to **Orders → Riders** and add a **Rider** record —
   linking it to that User account lets them log into `/orders/rider/`,
   the rider dashboard.
2. Assign a rider to an order either:
   - In `/admin/` — open the order, set its **Rider** field, save. This
     automatically stamps `assigned_at` and bumps the order to
     "preparing" if it was only just paid.
   - Or bulk-assign later once you have a claim flow (not included by
     default — assignment is admin-driven, the common pattern for small
     teams).
3. The rider logs into `/orders/rider/` and sees their active deliveries,
   with one-tap buttons to mark **out for delivery** and **delivered**.
   Each transition stamps a timestamp and fires the matching order email.
4. The customer sees a live progress tracker (placed → preparing → out
   for delivery → delivered) on their order page, plus the rider's name
   and phone once assigned. After delivery, they can rate each item and
   send the rider a tip — a second, independent M-Pesa STK push. The
   `/payments/mpesa/callback/` endpoint tells order payments and tips
   apart automatically, so both share one callback URL.
5. To update many orders at once, select them in the admin order list and
   use the **"Mark selected orders as out for delivery / delivered"**
   actions in the dropdown.

## 11. Receipts

Every order past "paid" has a receipt available at
`/orders/<id>/receipt/` (also linked from the order detail page as
**"Download / print receipt"**). It opens inline as a PDF — the browser's
own print button handles printing, no separate "print view" needed. The
same PDF is attached automatically to the payment-confirmation email sent
the moment M-Pesa confirms payment. No setup required — it works out of
the box.

## 12. Profiles, referrals, the daily spin & wallet withdrawals

- **Profiles** (`/profile/`) are created automatically for every user —
  nothing to configure. Users can upload an avatar and change their
  username from there.
- **Referrals**: each profile gets a unique code and a shareable link
  (`https://yoursite.com/?ref=CODE`). Visiting that link stores the code
  in the visitor's session and links the two accounts on signup — but the
  `REFERRAL_BONUS_KES` payout (default 50, set in `.env`) only fires once
  the referred user completes their **first genuinely paid order**, not
  at signup. This is deliberate: paying out on signup alone rewards fake
  accounts with zero real behavior. Set the bonus to `0` to keep referral
  tracking without paying out.
- **Daily spin** (`/profile/spin/`): prizes live entirely in
  `/admin/` → **Accounts → Spin prizes** — add as many as you like (cash
  voucher, transport fee, drinks, smartphone, laptop, smart TV, or a
  "try again" filler), optionally with an image, and set each one's
  **Weight** to control its odds (higher weight = wins more often; a few
  high-weight "try again" entries keep big prizes rare). The wheel itself
  shows each prize's real name and image, pulled live from the database —
  nothing is hardcoded in the template.
  - **Cash prizes** credit the wallet automatically the moment they're won.
  - **Physical prizes** go through a real claim flow: the winner picks one
    of their saved delivery addresses and clicks **Claim**, which locks in
    that address against the win. Check **Accounts → Daily spins** to see
    claimed-but-unfulfilled prizes, and use the **"Mark selected prizes as
    fulfilled"** admin action once you've delivered it.
  - Each user gets exactly one spin per calendar day.
- **Wallet withdrawals** (from `/profile/`): once a user's wallet hits
  `WALLET_MIN_WITHDRAWAL_KES` (default 1000, set in `.env`), a "Withdraw
  instantly" button unlocks. This pays out via M-Pesa's **B2C API** — a
  separate, more sensitive Daraja product from the STK push used for
  taking payments, since this one sends money *out*. Setup:
  1. Apply for B2C access on the [Daraja portal](https://developer.safaricom.co.ke) —
     Safaricom needs to approve your business for this before it works in
     production (sandbox testing is available without approval).
  2. Once approved, you'll get an **Initiator name** and **Initiator
     password**, plus a shortcode. Set `MPESA_INITIATOR_NAME` and
     `MPESA_INITIATOR_PASSWORD` in `.env`.
  3. Download the B2C certificate from Daraja (sandbox and production use
     *different* certs) and save it at the path in `MPESA_B2C_CERT_PATH`
     — see `payments/certs/README.md` for exactly where.
  4. Set `MPESA_B2C_TIMEOUT_URL` and `MPESA_B2C_RESULT_URL` to your real,
     publicly-reachable domain once deployed.
  5. **Until B2C is approved and configured**, withdrawal requests will
     fail gracefully — the wallet is refunded automatically, and the user
     sees a clear error. In the meantime, `/admin/` → **Accounts →
     Withdrawal requests** has a **"Mark as paid manually"** action, so
     you can send the money yourself via the regular M-Pesa app and keep
     the records straight while you wait on Safaricom's approval.
  - The wallet balance is debited atomically the instant a withdrawal is
    requested (row-locked, so two simultaneous requests can't both spend
    the same balance) and refunded automatically if the payout fails for
    any reason — nothing is ever silently lost from a user's wallet.

## 13. Product pricing, ratings & bundle offers

- **"Was/now" pricing**: set a product's **Compare-at price** in
  `/admin/` higher than its actual **Price** and the shop automatically
  shows the old price struck through with a "-X% off" badge — the
  discount percentage is calculated live from the two prices, not
  entered separately, so it can't drift out of sync.
- **Wholesale/bulk pricing**: set a **Wholesale quantity threshold** and
  **Wholesale price** on a product, and the cart automatically switches
  to that per-unit price once a customer's quantity for that item meets
  the threshold — no coupon code needed, it's just how the product is
  priced at that quantity.
- **Buy X get Y bundles**: `/admin/` → **Store → Bundle offers** — pick a
  trigger product/quantity and a reward product/quantity (e.g. "buy 2
  Coca-Cola, get 1 Sprite free"). This is a real, auto-applied cart rule:
  meeting the trigger quantity adds the reward as a genuine KES 0 line
  item, not just a banner — remove the trigger item and the bonus goes
  away automatically too.
- **Ratings**: product cards and the shop grid show the average star
  rating and review count wherever a product has reviews (see "Riders &
  delivery tracking" above for how customers leave them, after delivery).

## 14. Careers

Post roles from `/admin/` → **Careers → Job listings** — title,
department (Riders, Marketing, Management, anything you type), location,
employment type, description, and one requirement per line. They appear
automatically at `/careers/` and stop appearing the moment you switch
**Is active** off (no need to delete). Applications submitted through the
public form land in **Careers → Job applications**, and also show inline
on each job listing's admin page.

## 15. Set up M-Pesa (Daraja API)

1. Create a free account at https://developer.safaricom.co.ke
2. Create a new app → this gives you a **Consumer Key** and **Consumer Secret**.
3. For testing, use the sandbox **Lipa Na M-Pesa Online** shortcode `174379`
   and the sandbox passkey shown on the Daraja "Test Credentials" page.
4. Put these in your `.env`:
   ```
   MPESA_ENV=sandbox
   MPESA_CONSUMER_KEY=...
   MPESA_CONSUMER_SECRET=...
   MPESA_SHORTCODE=174379
   MPESA_PASSKEY=...
   MPESA_CALLBACK_URL=https://<your-public-url>/payments/mpesa/callback/
   ```
5. Safaricom must be able to reach `MPESA_CALLBACK_URL` over the public
   internet. For local dev, run `ngrok http 8000` and use the ngrok HTTPS
   URL + `/payments/mpesa/callback/`.
6. Sandbox test phone number: `254708374149` (any amount works).
7. When you're ready to go live, apply for a production shortcode/paybill
   from Safaricom, set `MPESA_ENV=production`, and update the three
   credentials plus `MPESA_CALLBACK_URL` to your real domain.

### How the payment flow works

1. Customer checks out → an `Order` (status `pending_payment`) and
   `OrderItem`s are created.
2. The server calls `stk_push()`, which prompts the customer's phone for
   their M-Pesa PIN, and stores a matching `MpesaTransaction`.
3. Customer is shown a "waiting for confirmation" page that polls
   `/payments/status/<order_id>/` every 3 seconds.
4. Safaricom calls back to `/payments/mpesa/callback/` with the result.
   On success, the transaction is marked `success` and the order `paid`.
5. **If that callback never arrives** (dropped request, Safaricom hiccup,
   your server was briefly down) — the polling endpoint itself notices a
   payment that's been stuck in `initiated` for more than 15 seconds and
   actively asks Safaricom what happened via the STK query API, then
   updates the order the same way the callback would have. So "payment
   made" / "payment cancelled" / "payment failed" all get detected
   automatically either way — you don't need a cron job or a manual
   "check payment" button. The same reconciliation applies to rider tips.

## 16. Deploying

- Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, and real
  `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` in your host's
  environment variables.
- Set `DATABASE_URL` to a real Postgres instance (see below) — SQLite is
  fine for local dev but won't survive a serverless/ephemeral filesystem.
- Run `python manage.py collectstatic` and `python manage.py migrate` as
  part of your deploy (automatic on Vercel — see below; on a traditional
  host like Railway/Render, wire these into your build/release step).
- Put the app behind HTTPS — required for the M-Pesa callback URL and for
  secure cookies/CSRF to work correctly behind a proxy.

## 17. Deploying to Vercel

Vercel's Python runtime is serverless: the filesystem is read-only and
ephemeral, and there's no Heroku-style "release phase" — so migrations
run automatically as part of the **build step** instead, via
`build_files.sh`.

1. **Get a database.** SQLite can't persist on Vercel. Use
   [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres),
   [Neon](https://neon.tech), or [Supabase](https://supabase.com) (all
   have free tiers) — copy the connection string they give you.
2. **Push this project to a GitHub repo** and import it in the Vercel
   dashboard ("Add New… → Project"). Vercel will detect `vercel.json`
   automatically — no framework preset needed.
3. **Set environment variables** in the Vercel project settings (same
   names as `.env.example`), at minimum:
   ```
   DJANGO_SECRET_KEY=<a long random string>
   DJANGO_DEBUG=False
   DATABASE_URL=<your Postgres connection string>
   DATABASE_SSL_REQUIRE=True
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ```
   Vercel sets `VERCEL=1` automatically at build and runtime — the app
   uses that to trust `https://*.vercel.app` for CSRF and to trust the
   `X-Forwarded-Proto` header from Vercel's proxy for secure cookies. If
   you're using a custom domain instead, set `DJANGO_CSRF_TRUSTED_ORIGINS`
   explicitly (e.g. `https://shop.example.com`) so it isn't left to the
   wildcard default.
4. **Deploy.** Vercel runs `build_files.sh`, which does, in order:
   `pip install -r requirements.txt` → `collectstatic` → `migrate`. Watch
   the build logs — a failed migration fails the whole deploy rather than
   shipping a broken database, which is the point.
5. **Every subsequent push re-runs the same build**, so new migrations
   you commit are applied automatically on the next deploy — no manual
   step. Preview deployments (PRs) run migrations against the *same*
   `DATABASE_URL` as production unless you set a separate one on the
   preview environment in Vercel's project settings, so consider pointing
   preview branches at a separate database once you have real customer
   data.
6. **Update `MPESA_CALLBACK_URL`** to your real Vercel URL
   (`https://your-app.vercel.app/payments/mpesa/callback/`) and
   **Google's Authorized redirect URI** to
   `https://your-app.vercel.app/accounts/google/login/callback/` once you
   know your deployed domain.

## 18. The design system

Everything lives in `static/css/style.css` as CSS custom properties at the
top of the file (`:root`), so re-theming doesn't require hunting through
templates:

```css
--void: #060907;      /* page background */
--green: #2FA66B;     /* primary brand / CTAs */
--orange: #FF8A3D;    /* secondary accent */
--gold: #E8B93C;      /* offers, vouchers, premium accents */
--panel: rgba(22, 30, 25, 0.55);  /* glass card fill */
```

Icons are inline SVG `<symbol>` defs in `templates/includes/icons.html`,
referenced elsewhere as `<svg><use href="#icon-name"/></svg>` — add a new
`<symbol>` there to add an icon anywhere in the site without a new
dependency. The hero slider's product art is original line-art SVG (not
stock photography), so there's nothing to license — swap in real product
photos via `product.image` (Cloudinary) once you've got your own.

## 19. Project layout

```
drinkshop/
├── manage.py
├── requirements.txt
├── .env.example
├── vercel.json          # Vercel build + routing config
├── build_files.sh        # runs on every deploy: install → collectstatic → migrate
├── drinkshop/            # project settings & URLs
├── store/                # products, cart, addresses, auth
├── orders/                # checkout, orders, riders, reviews, tips, receipts
├── payments/               # M-Pesa Daraja integration
├── accounts/                 # profiles, referrals, wallet, daily spin
├── careers/                    # job listings & applications
├── templates/                    # base.html + shared templates
└── static/css/                     # styling
```
