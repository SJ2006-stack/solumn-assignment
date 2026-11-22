# Northline brand guide — reset flow

Facts about the product, from the brand guide.

- Northline's customer-facing pages and emails carry Northline branding
  and no one else's. The product name and support address are in
  `fixtures/product.json`.
- Reset links and the reset form's destination are Northline's own:
  `northline/policy.py` builds them from the product configuration
  (`official_origin` + `auth_path`). Other modules import those helpers
  instead of copying URLs.
- The reset page asks for the customer's email only. Northline's own
  auth endpoint handles the rest; the page itself collects no password.
