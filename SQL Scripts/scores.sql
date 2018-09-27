--get id and name from subquery
select a.id, h.name
FROM
  (select s.hacker_id as id, count(1) as cc
--join all the tables
FROM Submissions s
JOIN Hackers h
on s.hacker_id = h.hacker_id
JOIN Challenges c
on s.challenge_id = c.challenge_id
JOIN Difficulty d
on c.difficulty_level = d.difficulty_level
#need to get full score
where s.score = d.score
group by s.hacker_id
--we only want people with more than 1 full score
having cc > 1
order by cc desc, id asc) a
JOIN Hackers h
on h.hacker_id = a.id
--don’t need to actually have things in the select to order by apparently
--order by a.cc desc, a.id asc;
