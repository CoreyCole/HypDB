WITH wights AS
  ( SELECT count(*)/N AS wight, Z
   FROM D
   GROUP BY Z),
            groups AS
  ( SELECT T, Z, avg(Y) AS intavg
   FROM D
   GROUP BY T,Z),
SELECT sum(lte*prob)
FROM groups,
     wights
WHERE groups.Z=wights.Z
GROUP BY T