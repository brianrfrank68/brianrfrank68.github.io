SELECT Pitching.Name,
                     Age,
       Tm,
       Pitching_Value.WAR,
       W,
       L,
       ERA,
       G,
       GS,
       SV,
       IP,
       H,
       R,
       ER,
       BB,
       SO,
       FIP,
       WHIP,
       H9,
       HR9,
       BB9,
       SO9,
       "SO/W",
       "Name-additional"
  FROM Pitching 
LEFT OUTER JOIN roster on Pitching."Name-additional" = roster.player_id
LEFT OUTER JOIN Pitching_Value on Pitching."Name-additional" = Pitching_Value."Name-additional"
WHERE roster.flb_team_init IS NULL
ORDER BY Pitching_Value.WAR DESC, Pitching."Name-additional"