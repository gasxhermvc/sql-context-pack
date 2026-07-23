# db-schema references

Owner-provided database DDL: tables, views, and procedures (for example `TABLE_ORDER.sql`, `UM_USER_Q.sql`).

Agents load matching files here as `FACT` before any SQL or data-touching work and must never infer a table, column, type, key, or constraint that is not present in a loaded reference. If the needed schema is missing, the agent names it and asks instead of guessing.
