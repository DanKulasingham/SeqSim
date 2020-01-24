SELECT Concat(Left(Right(Description,5),2),'-',(Cast(Left(Description,3) as float)*10)) As Description, Id
FROM Logs
WHERE Id < 104
ORDER BY MinLength,MinSED