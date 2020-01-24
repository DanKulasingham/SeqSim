Select SCBoards.CutplanID As ID, IsNull(LD.LogCount,Cutplans.PlannedLogsForCutplan) As "Log Count", SCBoards.Description From
		(Select LData.CutplanID As CutplanID, COUNT(LData.BoardVolume) As LogCount, SUM(LData.BoardVolume) As BoardVol FROM 
			(Select CutplanID, BoardVolume From LogData Where DateTime >= '@date1' and DateTime < '@date2') As LData Group by LData.CutplanID)
				As LD Full Outer Join SCBoards On LD.CutplanID = SCBoards.CutplanID Inner Join Cutplans On SCBoards.CutplanID = Cutplans.ID Where Cutplans.DateCreated >= '@date1' and Cutplans.DateCreated < '@date2'