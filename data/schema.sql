----------
-- TABLE: app
-- DESCRIPTION:
--   Primary table for application data. Usually will only hold one row
--   but it's possible to have several running applications for testing
--   or otherwise.
CREATE TABLE IF NOT EXISTS app (
    id TINYINT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status TINYINT NOT NULL,
    created INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now'))),
    updated INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now')))
);

-- EXAMPLE INSERT
-- INSERT INTO app
--     (name, status)
-- VALUES
--     ('main', 0),
--     ('test', 1)
-- ;
----------

----------
-- TABLE: hardware
-- DESCRIPTION:
--   This table contains rows for every piece of hardware the application(s)
--   need to keep track of, and what pins have been assigned to it.
CREATE TABLE IF NOT EXISTS hardware (
    id TINYINT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    app_id TINYINT NOT NULL,
    bcm_pin_write TINYINT NOT NULL,
    bcm_pin_read TINYINT NOT NULL,
    status TINYINT NOT NULL,
    active TINYINT NOT NULL DEFAULT 0,
    created INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now'))),
    updated INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now')))
);

-- EXAMPLE INSERT
-- INSERT INTO hardware
--     (name, app_id, bcm_pin_read, bcm_pin_write, status, active)
-- VALUES
--     ('door', 1, 22, 23, 0, 0),
--     ('light', 1, 17, 17, 0, 0)
-- ;
----------

----------
-- TABLE: astronomical
-- DESCRIPTION:
--   This table holds a row for every day that sunrise/sunset data has been
--   calculated for.
CREATE TABLE IF NOT EXISTS astronomical (
    id TINYINT PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    sunrise INTEGER NOT NULL,
    sunset INTEGER NOT NULL,
    day_length DECIMAL(2,3) NOT NULL,
    created INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now')))
);

-- EXAMPLE INSERT
-- INSERT INTO astronomical
--     (date, sunrise, sunset, day_length)
-- VALUES
--     ("2016-02-26", strftime('%s', '2016-02-26 06:54:43'),
--         strftime('%s', '2016-02-26 17:49:26'), 10.911)
-- ;
----------

----------
-- TRIGGER: updated_app
-- DESCRIPTION:
--   Updates a timestamp on the `app` table when changes occur
CREATE TRIGGER IF NOT EXISTS updated_app
AFTER UPDATE ON app
BEGIN
    UPDATE app
    SET updated = strftime('%s', DATETIME('now'))
    WHERE id = old.id;
END;
----------

----------
-- TRIGGER: updated_hardware
-- DESCRIPTION:
--   Updates a timestamp on the `hardware` table when changes occur
CREATE TRIGGER IF NOT EXISTS updated_hardware
AFTER UPDATE ON hardware
BEGIN
    UPDATE hardware
    SET updated = strftime('%s', DATETIME('now'))
    WHERE id = old.id;
END;
----------