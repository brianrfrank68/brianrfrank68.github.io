SELECT full_name,
       flb_team_init,
       Age,
       Tm,
       G,
       AB,
       R,
       H,
       "2B",
       "3B",
       HR,
       RBI,
       SB,
       CS,
       BB,
       SO,
       BA,
       OBP,
       SLG,
       OPS,
       "Pos Summary",
       Fielding."Pos Summary",
       "Name-additional"
  FROM roster
INNER JOIN Batting on Batting."Name-additional" = roster.player_id
LEFT OUTER JOIN Fielding on Fielding."Name-additional" = roster.player_id
ORDER BY flb_team_init, Batting."Name-additional"