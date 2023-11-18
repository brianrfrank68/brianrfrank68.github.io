SELECT full_name,
       flb_team_init
  FROM roster
LEFT OUTER JOIN Batting on Batting."Name-additional" = roster.player_id
LEFT OUTER JOIN Pitching on Pitching."Name-additional" = roster.player_id
WHERE Batting."Name-additional" IS NULL
AND Pitching."Name-additional" IS NULL
ORDER BY flb_team_init
