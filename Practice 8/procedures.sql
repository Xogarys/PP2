-- Procedure to insert or update a single contact
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name TEXT,   -- contact name
    p_phone TEXT,  -- contact phone
    p_email TEXT   -- contact email
)
LANGUAGE plpgsql AS $$
BEGIN
    -- If contact exists, update it
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts
        SET phone = p_phone, email = p_email
        WHERE name = p_name;
    ELSE
        -- If contact does not exist, insert a new one
        INSERT INTO contacts(name, phone, email)
        VALUES (p_name, p_phone, p_email);
    END IF;
END;
$$;


-- Procedure to insert multiple contacts
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    names TEXT[],   -- array of names
    phones TEXT[],  -- array of phones
    emails TEXT[]   -- array of emails
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;  -- loop counter
BEGIN
    -- Check if all arrays have the same length
    IF array_length(names,1) != array_length(phones,1)
       OR array_length(names,1) != array_length(emails,1) THEN
        RAISE EXCEPTION 'Array lengths mismatch';
    END IF;

    -- Loop through all contacts
    FOR i IN 1..array_length(names, 1) LOOP
        -- Validate phone format (+77xxxxxxxxx)
        IF phones[i] !~ '^\+77\d{9}$' THEN
            RAISE NOTICE 'Invalid phone: %', phones[i];  -- show warning
        ELSE
            -- Insert or update each contact
            CALL upsert_contact(names[i], phones[i], emails[i]);
        END IF;
    END LOOP;
END;
$$;


-- Procedure to delete a contact by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_value TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    -- Delete the contact
    DELETE FROM contacts
    WHERE name = p_value OR phone = p_value;
END;
$$;