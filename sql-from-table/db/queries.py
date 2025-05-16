def get_table_meta_query():
    return f""" WITH column_data AS (
    SELECT 
        table_schema,
        table_name,
        json_agg(
            json_build_object(
                'column_name', column_name,
                'data_type', data_type,
                'is_nullable', is_nullable,
                'max_length', character_maximum_length
            ) ORDER BY ordinal_position
        ) AS columns
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY table_schema, table_name
)
SELECT
    t.table_schema,
    t.table_name,
    obj_description(('"' || t.table_schema || '"."' || t.table_name || '"')::regclass, 'pg_class') AS table_description,
    pg_size_pretty(pg_total_relation_size(('"' || t.table_schema || '"."' || t.table_name || '"')::regclass)) AS total_size,
    (
        SELECT COUNT(*)
        FROM information_schema.columns c
        WHERE c.table_schema = t.table_schema AND c.table_name = t.table_name
    ) AS column_count,
    cd.columns
FROM information_schema.tables t
JOIN column_data cd 
    ON t.table_schema = cd.table_schema AND t.table_name = cd.table_name
WHERE t.table_type = 'BASE TABLE' 
  AND t.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(('"' || t.table_schema || '"."' || t.table_name || '"')::regclass) DESC;
"""


def get_table_rels():
    return f"""

SELECT
    tc.table_schema,
    tc.table_name AS source_table,
    kcu.column_name AS source_column,
    ccu.table_name AS target_table,
    ccu.column_name AS target_column
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY';
"""
