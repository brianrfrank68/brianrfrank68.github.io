SELECT Batting.Name
       Age,
       Tm,
       Batting_Value.WAR,
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
  FROM Batting 
LEFT OUTER JOIN roster on Batting."Name-additional" = roster.player_id
LEFT OUTER JOIN Batting_Value on Batting."Name-additional" = Batting_Value."Name-additional"
LEFT OUTER JOIN Fielding on Fielding."Name-additional" = Batting."Name-additional"
WHERE roster.flb_team_init IS NULL
ORDER BY Batting_Value.WAR DESC, Fielding."Pos Summary", Batting."Name-additional"