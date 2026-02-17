-- Database Anonymization Script
-- Replaces personal data in res_partner with fake data.
-- Preserves system partners (id <= 3) and the admin user.

BEGIN;

-- Anonymize partner names (skip system partners)
UPDATE res_partner
SET name = 'Partner ' || id,
    email = 'partner_' || id || '@example.com',
    phone = '+1-555-' || LPAD(id::text, 4, '0'),
    mobile = NULL,
    street = id || ' Example Street',
    street2 = NULL,
    city = 'Example City',
    zip = '00000',
    website = NULL,
    comment = NULL,
    vat = NULL
WHERE id > 3;

-- Reset all user passwords to 'admin' (except public/portal users)
UPDATE res_users
SET password = 'admin'
WHERE id > 2
  AND active = true;

-- Clear email addresses from mail aliases
UPDATE mail_alias
SET alias_contact = 'everyone'
WHERE id > 0;

COMMIT;
