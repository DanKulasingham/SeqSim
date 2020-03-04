Select CD.ID, CD.Logs as "Log Count", Cutplans.Description From 
	(Select Min(DateTime) as StartTime, CutplanID as ID, Count(*) as Logs From LogData Where DateTime >= '@date1' and DateTime < '@date2' Group by CutplanID)
		as CD inner join Cutplans on CD.ID = Cutplans.ID order by StartTime asc