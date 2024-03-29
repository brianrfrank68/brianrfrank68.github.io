
SELECT 
pitching.Name,
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
       Pitching_Value.WAR,
       W,
       L,
       ERA,
       G,
       GS,
       GF,
       CG,
       SHO,
       SV,
       IP,
       H,
       R,
       ER,
       HR,
       BB,
       IBB,
       SO,
       FIP,
       WHIP,
       H9,
       HR9,
       BB9,
       SO9,
       "SO/W",
       pitching."Name-additional"
  FROM pitching
LEFT OUTER JOIN roster on pitching."Name-additional" = roster.player_id
LEFT OUTER JOIN Pitching_Value on pitching."Name-additional" = Pitching_Value."Name-additional"
LEFT OUTER JOIN Fielding on Fielding."Name-additional" = pitching."Name-additional"
LEFT OUTER JOIN player_list on player_list.player_id = pitching."Name-additional"
LEFT OUTER JOIN Dynasty_October on (player_list.player_name = Dynasty_October.Player OR Dynasty_October.Player = player_list.alt_name)
LEFT OUTER JOIN Dynasty_Prospect_October on (player_list.player_name = Dynasty_Prospect_October.Player OR Dynasty_Prospect_October.Player = player_list.alt_name)
LEFT OUTER JOIN Dynasty_Prospect_March on (player_list.player_name = Dynasty_Prospect_March.Player OR Dynasty_Prospect_March.Player = player_list.alt_name)
  --inner join fielding on fielding.player_id = pitchers.player_id
 WHERE
  roster.flb_team_init IS NULL
  
ORDER BY CAST(Dynasty_October.Rank AS INT) ASC NULLS LAST, 
CAST(Dynasty_Prospect_October.Rank AS INT) ASC NULLS LAST, 
CAST(Dynasty_Prospect_March.Rank AS INT) ASC NULLS LAST, 
Pitching_Value.WAR DESC, pitching."Name-additional"

  

