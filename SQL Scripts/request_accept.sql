select aa.id as id, sum(aa.counter) as num
FROM
  ((select a.requester_id as id, ifnull(count(a.requester_id),0) as counter
  FROM request_accepted a
  group by 1)
  union all
  (select b.accepter_id as id, ifnull(count(b.accepter_id),0) as counter
  FROM request_accepted b
  group by 1)) aa
group by id
order by num desc
limit 1;
