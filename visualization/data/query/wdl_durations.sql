
WITH events AS (
	SELECT 
		e.match_id,
		e.type_name,
		e.player_name,
		CASE WHEN type_name NOT IN ('Half Start', 'Half End') THEN e.team_name END AS team_name,
		e.period,
		e.timestamp,
		e.minute,
		e.second,
		e.duration, 
		ROW_NUMBER() OVER (PARTITION BY e.match_id) as match_rnk,
		ADDTIME(STR_TO_DATE(timestamp, '%H:%i:%s.%f'), SEC_TO_TIME(e.duration)) as new_timestamp,
		m.home_team_name,
		m.away_team_name
	FROM event_stg e
	JOIN `match` m
	ON e.match_id = m.match_id
	WHERE
		e.outcome_name = 'Goal'
		OR e.type_name = 'Half Start' AND (e.team_name != e.possession_team_name)
		OR (e.type_name = 'Half End') AND (e.team_name != e.possession_team_name)
	ORDER BY 
		e.match_id DESC, 
		e.period, 
		e.timestamp
	),
scored_goals as (
	SELECT e.*, 
		CASE
			WHEN team_name = home_team_name THEN 1
			WHEN team_name = away_team_name THEN -1
			ELSE 0
		END AS goal_effect
	FROM EVENTS e
	),
cumulative_score AS (
    SELECT
        s.*,
        -- Her maç ve yarı için kümülatif skor farkını hesaplama
        SUM(s.goal_effect) OVER (
            PARTITION BY s.match_id
            ORDER BY s.period asc, s.timestamp asc
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS score_difference
    FROM scored_goals s
	),
match_status AS (
	SELECT *,
    CASE 
		WHEN score_difference > 0 THEN '1' -- indicates home win
        WHEN score_difference < 0 THEN '2' -- indicates away win
        ELSE '0' -- indicates draw
        END AS status,
	LEAD(new_timestamp,1) OVER ( PARTITION BY match_id, period ORDER BY period, timestamp) as lagger
    FROM cumulative_score
	),
time_diff AS (
SELECT *, TIMEDIFF(lagger, new_timestamp ) as diff
FROM match_status
),
home_duration_split AS (
    SELECT 
        home_team_name,
        match_id,
        CASE WHEN status = '1' THEN TIME_TO_SEC(TIME_FORMAT(`diff`, "%H:%i:%s")) ELSE 0 END AS win_duration,
        CASE WHEN status = '0' THEN TIME_TO_SEC(TIME_FORMAT(`diff`, "%H:%i:%s")) ELSE 0 END AS draw_duration,
        CASE WHEN status = '2' THEN TIME_TO_SEC(TIME_FORMAT(`diff`, "%H:%i:%s")) ELSE 0 END AS lose_duration
    FROM time_diff
),
away_duration_split AS (
    SELECT 
        away_team_name,
        match_id,
        CASE WHEN status = '2' THEN TIME_TO_SEC(TIME_FORMAT(`diff`, "%H:%i:%s")) ELSE 0 END AS win_duration,
        CASE WHEN status = '0' THEN TIME_TO_SEC(TIME_FORMAT(`diff`, "%H:%i:%s")) ELSE 0 END AS draw_duration,
        CASE WHEN status = '1' THEN TIME_TO_SEC(TIME_FORMAT(`diff`, "%H:%i:%s")) ELSE 0 END AS lose_duration
    FROM time_diff
)
SELECT
	h.home_team_name as team_name,
	h.match_count_h + a.match_count_a AS match_count,
    h.win_duration_h + a.win_duration_a AS win_duration,
    h.draw_duration_h + a.draw_duration_a AS draw_duration,
    h.lose_duration_h + a.lose_duration_a AS lose_duration,
    h.total_mins_played_h + a.total_mins_played_a AS total_mins_played
FROM (
	SELECT
			home_team_name,
			SUM(win_duration) AS win_duration_h,
			SUM(draw_duration) AS draw_duration_h,
			SUM(lose_duration) AS lose_duration_h,
			SUM(win_duration+draw_duration+lose_duration) AS total_mins_played_h,
			COUNT(DISTINCT match_id) AS match_count_h
		FROM home_duration_split
		GROUP BY home_team_name
		ORDER BY home_team_name
	) h
LEFT JOIN (
	SELECT
		away_team_name,
		SUM(win_duration) AS win_duration_a,
		SUM(draw_duration) AS draw_duration_a,
		SUM(lose_duration) AS lose_duration_a,
		SUM(win_duration+draw_duration+lose_duration) AS total_mins_played_a,
		COUNT(DISTINCT match_id) AS match_count_a
	FROM away_duration_split
	GROUP BY away_team_name
	ORDER BY away_team_name 
	) a
ON h.home_team_name = a.away_team_name
ORDER BY win_duration DESC