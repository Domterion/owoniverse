CREATE TABLE IF NOT EXISTS settings (
    "id" BIGINT PRIMARY KEY,
    "log" BIGINT,
    "prefix" VARCHAR(20),
    "mod_logs" BOOLEAN DEFAULT TRUE,
    "message_logs" BOOLEAN DEFAULT TRUE,
    "member_logs" BOOLEAN DEFAULT TRUE,
    "guild_logs" BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cases (
    "id" SERIAL PRIMARY KEY,
    "guild" BIGINT REFERENCES settings(id) ON DELETE CASCADE,
    "action" VARCHAR(15) NOT NULL,
    "mod" BIGINT NOT NULL,
    "user" BIGINT NOT NULL,
    "reason" VARCHAR(512) NOT NULL,
    "time" TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);