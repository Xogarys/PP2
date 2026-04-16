-- Function to search contacts by keyword
CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(name TEXT, phone TEXT, email TEXT) AS $$
BEGIN
    -- Return all contacts where name, phone, or email matches the keyword (case-insensitive)
    RETURN QUERY
    SELECT c.name, c.phone, c.email
    FROM contacts c
    WHERE c.name ILIKE '%' || p || '%'   -- search in name
       OR c.phone ILIKE '%' || p || '%'  -- search in phone
       OR c.email ILIKE '%' || p || '%'; -- search in email
END;
$$ LANGUAGE plpgsql;


-- Function to get contacts with pagination
CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_val INT, offset_val INT)
RETURNS TABLE(name TEXT, phone TEXT, email TEXT) AS $$
BEGIN
    -- Return a limited number of contacts, skipping some rows
    RETURN QUERY
    SELECT c.name, c.phone, c.email
    FROM contacts c
    LIMIT limit_val    -- number of rows to return
    OFFSET offset_val; -- number of rows to skip
END;
$$ LANGUAGE plpgsql;