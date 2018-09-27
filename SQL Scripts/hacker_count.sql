select gr.hacker_id, hh.name, gr.counted
FROM
(select h.hacker_id, count(challenge_id) as counted
FROM Hackers h
JOIN
Challenges c
on h.hacker_id = c.hacker_id
group by 1) gr
JOIN Hackers hh
on gr.hacker_id = hh.hacker_id
WHERE gr.counted = 50
or gr.counted in (
	—get all counts that have a total of 1
        select m.num
        FROM
        (
	— of all the counts, count how many times they show up, and filter out anything greater than 1 (besides the max number)
	 select q.counted as num, count(1) as tot
        from
        (select h.hacker_id, count(challenge_id) as counted
        FROM Hackers h
        JOIN
        Challenges c
        on h.hacker_id = c.hacker_id
        group by 1
        having counted != max(counted)) q
        group by 1
        having tot = 1) m)
ORDER BY gr.counted desc, hacker_id;
