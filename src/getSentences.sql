WITH RankedCalls AS (
    SELECT 
        JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.phone_number')) AS phone_number,
        JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.sentence')) AS sentence,
        JSON_EXTRACT(call_data, '$.iscall_start') AS iscall_start,
        JSON_EXTRACT(call_data, '$.iscall_end') AS iscall_end,
        ROW_NUMBER() OVER (PARTITION BY JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.phone_number')) ORDER BY id) AS rn
    FROM PhoneCalls
),
CallStarts AS (
    SELECT phone_number, MIN(rn) AS start_rn
    FROM RankedCalls
    WHERE iscall_start = TRUE
    GROUP BY phone_number
),
CallEnds AS (
    SELECT phone_number, MIN(rn) AS end_rn
    FROM RankedCalls
    WHERE iscall_end = FALSE AND rn > (SELECT start_rn FROM CallStarts WHERE CallStarts.phone_number = RankedCalls.phone_number)
    GROUP BY phone_number
)
SELECT 
    r.phone_number,
    GROUP_CONCAT(r.sentence ORDER BY r.rn SEPARATOR ' ') AS conversation
FROM RankedCalls r
JOIN CallStarts s ON r.phone_number = s.phone_number
LEFT JOIN CallEnds e ON r.phone_number = e.phone_number
WHERE r.rn >= s.start_rn AND (e.end_rn IS NULL OR r.rn <= e.end_rn)
GROUP BY r.phone_number;