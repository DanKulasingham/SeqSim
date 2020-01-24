Select
	CPSched.CutPlanIDD As CutplanID, CPSched.Description As Description,CPSched.LogCount As LogCount,CPSched.BoardVol As BoardVol, FCBoards.FCOuterWidth As PrimOutWidth, FCBoards.FCOuterThick As PrimOutThick, FCBoards.FCInnerWidth As PrimInWidth, FCBoards.FCInnerThick As PrimInThick,
	FCBoards.SawkerfOuterSaw As PrimOutK, FCBoards.SawkerfInnerSaw As PrimInK, FCBoards.SawKerfSplitSaw As PrimSplitK, FCBoards.FCSplitOuterBoard As PrimOutSplit, FCBoards.FCSplitInnerBoard As PrimInSplit,
	CPSched.SCCenterBoardWidth As CBWidth, CPSched.SCBoard1Thick As CBThick1, CPSched.SCBoard2Thick As CBThick2, CPSched.SCBoard3Thick As CBThick3, CPSched.SCBoard4Thick As CBThick4, CPSched.SCBoard5Thick As CBThick5,
	CPSched.SCBoard6Thick As CBThick6, CPSched.SCBoard7Thick As CBThick7, CPSched.SCBoard8Thick As CBThick8, CPSched.SCBoard9Thick As CBThick9, CPSched.SCBoard10Thick As CBThick10, CPSched.NrOfCenterBoards As CBNum,
	CPSched.SCProfileOuterWidth As SecOutWidth, CPSched.SCProfileOuterLHThickness As SecOutThickT, CPSched.SCProfileOuterRHThickness As SecOutThickB, CPSched.SCProfileInnerWidth As SecInWidth, CPSched.SCProfileInnerLHThickness As SecInThickT,
	CPSched.SCProfileInnerRHThickness As SecInThickB, CPSched.SawKerfSC As SecK, CPSched.SplitSCBoardOuterLH As SecOutSplitT, CPSched.SplitSCBoardOuterRH As SecOutSplitB, CPSched.SplitSCBoardInnerLH As SecInSplitT, CPSched.SplitSCBoardInnerRH As SecInSplitB,
	CPSched.HoriSawsLeft As HSNum, CPSched.HoriLeftWidth1 As HorWidth1, CPSched.HoriLeftWidth2 As HorWidth2, CPSched.HoriLeftWidth3 As HorWidth3, CPSched.HoriLeftWidth4 As HorWidth4, CPSched.SawKerfHoriLeft1 As HSK1,
	CPSched.SawKerfHoriLeft2 As HSK2, CPSched.SawKerfHoriLeft3 As HSK3
	From 
	
	(Select SCBoards.CutplanID As CutplanIDD, IsNull(LD.LogCount,Cutplans.PlannedLogsForCutplan) As LogCount, IsNull(LD.BoardVol, 0) As BoardVol, SCBoards.* From
		(Select LData.CutplanID As CutplanID, COUNT(LData.BoardVolume) As LogCount, SUM(LData.BoardVolume) As BoardVol FROM 
			(Select CutplanID, BoardVolume From LogData Where CutplanID = @CPID) As LData Group by LData.CutplanID)
				As LD Full Outer Join SCBoards On LD.CutplanID = SCBoards.CutplanID Inner Join Cutplans On SCBoards.CutplanID = Cutplans.ID Where Cutplans.ID = @CPID) As
	
	CPSched Inner Join FCBoards On CPSched.CutPlanID = FCBoards.CutPlanID 