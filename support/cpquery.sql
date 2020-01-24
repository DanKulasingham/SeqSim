Select CD.*, Cutplans.Description From 
	(Select CutplanID as ID, Count(*) as "Log Count" From LogData Where DateTime >= '@date1' and DateTime < '@date2' Group by CutplanID)
		as CD inner join Cutplans on CD.ID = Cutplans.ID