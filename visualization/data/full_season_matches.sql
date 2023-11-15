/*
helps me finding out available full season data on statsbomb's open data.
because I want to include full season statistics in analyses, I'll work on particular seasons that all matches are available in the open data.
*/
SELECT
	a.home_team_name
	, a.season_name
	, a.competition_name
	, a.match_count_home + b.match_count_away as match_count
	, c.season_match_count
FROM (
	SELECT 
		m.home_team_name
		,  m.season_name
		, m.competition_name
		, COUNT(DISTINCT match_id)  AS match_count_home
	FROM match m
	GROUP BY home_team_id, season_id
	) a
JOIN (
	SELECT 
		m.away_team_name
		,  m.season_name
		, m.competition_name
		, count(DISTINCT match_id)  AS match_count_away
	FROM match m
	GROUP BY away_team_id, season_id
	)  b
ON a.home_team_name = b.away_team_name
AND a.season_name = b.season_name
AND a.competition_name = b.competition_name
LEFT JOIN  (
	SELECT season_name, competition_name, COUNT(DISTINCT match_id) as season_match_count
	FROM match m
	GROUP BY season_id,competition_id
	) c
ON a.season_name = c.season_name
AND a.competition_name  = c.competition_name
ORDER BY 5 DESC,4 DESC,3, 2 DESC
;


