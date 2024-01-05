SELECT Batting.Name,
roster.flb_team_init,
       Age,
       Dynasty_October.Rank,
--       Dynasty_October.Prospect,
       Dynasty_October."POS.",
       Dynasty_October."SEC. POS.",
       Dynasty_Prospect_October.Rank,
       Dynasty_Prospect_October."POS.",
       Dynasty_Prospect_October."SEC. POS.",
       Dynasty_Prospect_March.Rank,
       Dynasty_Prospect_March."POS.",
       Dynasty_Prospect_March."SEC. POS.",
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
       --Fielding."Pos Summary",
       "Name-additional"
  FROM Batting 
LEFT OUTER JOIN roster on Batting."Name-additional" = roster.player_id
LEFT OUTER JOIN Batting_Value on Batting."Name-additional" = Batting_Value."Name-additional"
LEFT OUTER JOIN Fielding on Fielding."Name-additional" = Batting."Name-additional"
LEFT OUTER JOIN player_list on player_list.player_id = Batting."Name-additional"
LEFT OUTER JOIN Dynasty_October on (player_list.player_name = Dynasty_October.Player OR Dynasty_October.Player = player_list.alt_name)
LEFT OUTER JOIN Dynasty_Prospect_October on (player_list.player_name = Dynasty_Prospect_October.Player OR Dynasty_Prospect_October.Player = player_list.alt_name)
LEFT OUTER JOIN Dynasty_Prospect_March on (player_list.player_name = Dynasty_Prospect_March.Player OR Dynasty_Prospect_March.Player = player_list.alt_name)
WHERE 
(
Batting."Pos Summary" LIKE '9%'
OR Batting."Pos Summary" LIKE '*9%'
OR Batting."Pos Summary" LIKE '/9%'
)
AND roster.flb_team_init IS NULL
ORDER BY CAST(Dynasty_October.Rank AS INT) ASC NULLS LAST, 
CAST(Dynasty_Prospect_October.Rank AS INT) ASC NULLS LAST, 
CAST(Dynasty_Prospect_March.Rank AS INT) ASC NULLS LAST, 
Batting_Value.WAR DESC, Batting."Name-additional"