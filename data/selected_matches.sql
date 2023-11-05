/* selects all lineup data in selected player's available matches.*/

SELECT m.*
	, l. player_id
	, l.player_name
	, l.player_nickname
	, l.jersey_number
	, l.team_id
	, l.team_name
	, l.country_id
	, l.country_name as country_name_lineup
FROM (
	SELECT *
	FROM match
	WHERE season_id = 26
	) m

LEFT JOIN (
	SELECT a.*
	FROM lineup a
	LEFT JOIN 
		(
			SELECT DISTINCT match_id
			FROM lineup
			WHERE player_id = 5503
			)  b
	ON a.match_id =  b.match_id
	WHERE b.match_id IS NOT NULL
	)  l
ON m.match_id = l. match_id

