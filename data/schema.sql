----------
-- TABLE: app
-- DESCRIPTION:
--   Primary table for application data. Usually will only hold one row
--   but it's possible to have several running applications for testing
--   or otherwise.
CREATE TABLE IF NOT EXISTS app (
    app_id TINYINT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    latitude DECIMAL (10, 8) NOT NULL,
    longitude DECIMAL (10, 8) NOT NULL,
    ideal_daylight_hours TINYINT NOT NULL,
    timezone TEXT NOT NULL,
    status TINYINT NOT NULL,
    created INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now'))),
    updated INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now')))
);

-- EXAMPLE INSERT
-- INSERT INTO app
--     (name, latitude, longitude, ideal_daylight_hours, timezone, status)
-- VALUES
--     ('main', 47.690416, -122.315576, 13, 'America/Los_Angeles', 0),
--     ('test', 47.690416, -122.315576, 13, 'America/Los_Angeles', 1)
-- ;
----------

----------
-- TABLE: hardware
-- DESCRIPTION:
--   This table contains rows for every piece of hardware the application(s)
--   need to keep track of, and what pins have been assigned to it.
CREATE TABLE IF NOT EXISTS hardware (
    hardware_id TINYINT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    app_id TINYINT NOT NULL,
    bcm_pin_write TINYINT NOT NULL,
    bcm_pin_read TINYINT NOT NULL,
    status TINYINT NOT NULL,
    created INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now'))),
    updated INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now')))
);

-- EXAMPLE INSERT
-- INSERT INTO hardware
--     (name, app_id, bcm_pin_read, bcm_pin_write, status)
-- VALUES
--     ('door', 1, 22, 23, 0),
--     ('light', 1, 17, 17, 0)
-- ;
----------

----------
-- TABLE: astronomical
-- DESCRIPTION:
--   This table holds a row for every day that sunrise/sunset data has been
--   calculated for.
CREATE TABLE IF NOT EXISTS astronomical (
    astronomical_id TINYINT PRIMARY KEY,
    sunrise INTEGER NOT NULL,
    sunset INTEGER NOT NULL,
    daylight_hours DECIMAL(2,3) NOT NULL,
    created INTEGER NOT NULL DEFAULT (strftime('%s', DATETIME('now')))
);

-- EXAMPLE INSERT
-- INSERT INTO astronomical
--     (sunrise, sunset, daylight_hours)
-- VALUES
--     (strftime('%s', '2016-02-26 06:54:43'),
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
    WHERE app_id = old.app_id;
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
    WHERE hardware_id = old.hardware_id;
END;
----------
