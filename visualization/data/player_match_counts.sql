/* Catalog for choosing the players with enough matches in a season*/
WITH JOINT AS (
SELECT	m.competition_id
        , m.competition_name
        , m.season_id
        , m.season_name
        , l.*
FROM lineup l
LEFT JOIN match m
ON m.match_id = l.match_id
)

SELECT *
FROM (
	SELECT  player_id
			, player_nickname
			, team_id
			, team_name
			, season_id
			, season_name
			, count() OVER (PARTITION BY player_id, team_id, season_id) AS match_count_breakdown
			, count() OVER (PARTITION BY player_id) AS match_count
	FROM joint
	)
GROUP BY player_id, team_id, season_id
ORDER BY 8 DESC, 1, 6 DESC