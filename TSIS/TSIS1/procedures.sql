-- ============================================================
--  PhoneBook TSIS 1 — Stored Procedures & Functions
--  Safe re-run version
-- ============================================================


-- ============================================================
-- DROP old objects first
-- ============================================================

DROP PROCEDURE IF EXISTS upsert_contact(TEXT, TEXT, TEXT);
DROP PROCEDURE IF EXISTS bulk_insert_contacts(TEXT[], TEXT[], TEXT[]);
DROP PROCEDURE IF EXISTS delete_contact(TEXT);
DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR);

DROP FUNCTION IF EXISTS get_contacts_paginated(INT, INT);
DROP FUNCTION IF EXISTS search_contacts(TEXT);


-- ============================================================
-- Add / update contact
-- ============================================================

CREATE PROCEDURE upsert_contact(
    p_name  TEXT,
    p_phone TEXT,
    p_email TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id INTEGER;
BEGIN

    SELECT id
    INTO v_id
    FROM contacts
    WHERE name = p_name;

    IF v_id IS NOT NULL THEN

        UPDATE contacts
        SET email = p_email
        WHERE id = v_id;

        IF NOT EXISTS (
            SELECT 1
            FROM phones
            WHERE contact_id = v_id
            AND phone = p_phone
        ) THEN

            INSERT INTO phones(
                contact_id,
                phone,
                type
            )
            VALUES (
                v_id,
                p_phone,
                'mobile'
            );

        END IF;

    ELSE

        INSERT INTO contacts(
            name,
            email
        )
        VALUES (
            p_name,
            p_email
        )
        RETURNING id INTO v_id;

        INSERT INTO phones(
            contact_id,
            phone,
            type
        )
        VALUES (
            v_id,
            p_phone,
            'mobile'
        );

    END IF;

END;
$$;


-- ============================================================
-- Bulk insert
-- ============================================================

CREATE PROCEDURE bulk_insert_contacts(
    names TEXT[],
    phones_arr TEXT[],
    emails TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
BEGIN

    IF array_length(names,1) != array_length(phones_arr,1)
    OR array_length(names,1) != array_length(emails,1) THEN

        RAISE EXCEPTION 'Array lengths mismatch';

    END IF;


    FOR i IN 1..array_length(names,1)
    LOOP

        IF phones_arr[i] !~ '^\+77\d{9}$' THEN

            RAISE NOTICE
            'Invalid phone skipped: %',
            phones_arr[i];

        ELSE

            CALL upsert_contact(
                names[i],
                phones_arr[i],
                emails[i]
            );

        END IF;

    END LOOP;

END;
$$;


-- ============================================================
-- Delete contact
-- ============================================================

CREATE PROCEDURE delete_contact(
    p_value TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    DELETE FROM contacts
    WHERE name = p_value
    OR id IN (
        SELECT contact_id
        FROM phones
        WHERE phone = p_value
    );

END;
$$;


-- ============================================================
-- Pagination
-- ============================================================

CREATE FUNCTION get_contacts_paginated(
    limit_val INT,
    offset_val INT
)
RETURNS TABLE(
    name TEXT,
    phone TEXT,
    email TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY

    SELECT DISTINCT ON (c.name)
        c.name::TEXT,
        p.phone::TEXT,
        c.email::TEXT
    FROM contacts c
    LEFT JOIN phones p
        ON p.contact_id = c.id
    ORDER BY c.name
    LIMIT limit_val
    OFFSET offset_val;

END;
$$;


-- ============================================================
-- Add phone
-- ============================================================

CREATE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id INTEGER;
BEGIN

    SELECT id
    INTO v_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_id IS NULL THEN

        RAISE EXCEPTION
        'Contact "%" not found',
        p_contact_name;

    END IF;


    IF p_type NOT IN (
        'home',
        'work',
        'mobile'
    ) THEN

        RAISE EXCEPTION
        'Phone type must be home, work, or mobile';

    END IF;


    INSERT INTO phones(
        contact_id,
        phone,
        type
    )
    VALUES (
        v_id,
        p_phone,
        p_type
    );

END;
$$;


-- ============================================================
-- Move to group
-- ============================================================

CREATE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN

    SELECT id
    INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN

        RAISE EXCEPTION
        'Contact "%" not found',
        p_contact_name;

    END IF;


    SELECT id
    INTO v_group_id
    FROM groups
    WHERE name = p_group_name;


    IF v_group_id IS NULL THEN

        INSERT INTO groups(name)
        VALUES (p_group_name)
        RETURNING id INTO v_group_id;

    END IF;


    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

END;
$$;


-- ============================================================
-- Search
-- ============================================================

CREATE FUNCTION search_contacts(
    p_query TEXT
)
RETURNS TABLE(
    name TEXT,
    phone TEXT,
    email TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY

    SELECT DISTINCT
        c.name::TEXT,
        ph.phone::TEXT,
        c.email::TEXT
    FROM contacts c
    LEFT JOIN phones ph
        ON ph.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
    OR c.email ILIKE '%' || p_query || '%'
    OR ph.phone ILIKE '%' || p_query || '%';

END;
$$;