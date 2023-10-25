/* Retrieve all matches and lineups for the target season & player  */
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
		SELECT *
		FROM JOINT
		WHERE 1=1
		AND season_id = 26
--		AND player_id = 5503
	) J
LEFT OUTER JOIN match m 
USING (match_id)
WHERE J.MATCH_ID IS NOT NULL
