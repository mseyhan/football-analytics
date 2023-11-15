SELECT   home_team_name,home_team_id as team_id, home_team_country_name
FROM match m
LEFT JOIN competition c
ON c.competition_id = m.competition_id
WHERE c.competition_gender = 'male'
GROUP BY home_team_country_name, home_team_name

UNION

SELECT  away_team_name, away_team_id, away_team_country_name
FROM MATCH m
LEFT JOIN competition c
ON c.competition_id = m.competition_id
WHERE c.competition_gender = 'male'
GROUP BY away_team_country_name, away_team_name
ORDER BY 1,2,3
;