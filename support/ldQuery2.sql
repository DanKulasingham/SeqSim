SELECT Top 1000 LogData.Length, LogData.SED, LogData.MinSED, LogData.LED, LogData.LED As MaxLED, (LogData.Sweep*LogData.SED)/100 as Sweep, LogData.CompoundSweep AS CompSweep, LogData.Volume As Vol From LogData Inner Join Cutplans On LogData.CutplanID = Cutplans.ID
	Where Concat(Right(Left(Cutplans.Description,4),2),'-', Right(Left(Cutplans.Description,7),2)) = '@sort'
	Order by DateTime Desc