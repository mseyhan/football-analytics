/* Retrieve all matches and lineups for the target season*/
SELECT m.*
    , l.player_id
    , l.player_name
    , l.player_nickname
    , l.jersey_number
    , l.team_id
    , l.team_name
    , l.country_id
    , l.country_name as country_name_lineup
FROM (
    SELECT *
    FROM `MATCH` m
    WHERE 1=1
    AND season_id = 27
    AND competition_id = 2 -- if it's necessary to see the picture regardless the competition through the season, just comment out.
) m
LEFT JOIN lineup l
ON m.match_id = l.match_id