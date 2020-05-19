CREATE TABLE IF NOT EXISTS settings (
    "id" BIGINT PRIMARY KEY,
    "log" BIGINT,
    "prefix" VARCHAR(20),
    "mod_logs" BOOLEAN DEFAULT TRUE,
    "message_logs" BOOLEAN DEFAULT TRUE,
    "member_logs" BOOLEAN DEFAULT TRUE,
    "guild_logs" BOOLEAN DEFAULT TRUE
)